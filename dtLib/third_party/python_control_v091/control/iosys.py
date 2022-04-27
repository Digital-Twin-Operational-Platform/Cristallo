# iosys.py - input/output system module
#
# RMM, 28 April 2019
#
# Additional features to add
#   * Allow constant inputs for MIMO input_output_response (w/out ones)
#   * Add support for constants/matrices as part of operators (1 + P)
#   * Add unit tests (and example?) for time-varying systems
#   * Allow time vector for discrete time simulations to be multiples of dt
#   * Check the way initial outputs for discrete time systems are handled
#

"""The :mod:`~control.iosys` module contains the
:class:`~control.InputOutputSystem` class that represents (possibly nonlinear)
input/output systems.  The :class:`~control.InputOutputSystem` class is a
general class that defines any continuous or discrete time dynamical system.
Input/output systems can be simulated and also used to compute equilibrium
points and linearizations.

"""

__author__ = "Richard Murray"
__copyright__ = "Copyright 2019, California Institute of Technology"
__credits__ = ["Richard Murray"]
__license__ = "BSD"
__maintainer__ = "Richard Murray"
__email__ = "murray@cds.caltech.edu"

import numpy as np
import scipy as sp
import copy
from warnings import warn

from .statesp import StateSpace, tf2ss, _convert_to_statespace
from .xferfcn import TransferFunction
from .timeresp import _check_convert_array, _process_time_response, \
    TimeResponseData
from .lti import isctime, isdtime, common_timebase
from . import config

__all__ = ['InputOutputSystem', 'LinearIOSystem', 'NonlinearIOSystem',
           'InterconnectedSystem', 'LinearICSystem', 'input_output_response',
           'find_eqpt', 'linearize', 'ss2io', 'tf2io', 'interconnect',
           'summing_junction']

# Define module default parameter values
_iosys_defaults = {
    'iosys.state_name_delim': '_',
    'iosys.duplicate_system_name_prefix': '',
    'iosys.duplicate_system_name_suffix': '$copy',
    'iosys.linearized_system_name_prefix': '',
    'iosys.linearized_system_name_suffix': '$linearized'
}


class InputOutputSystem(object):
    """A class for representing input/output systems.

    The InputOutputSystem class allows (possibly nonlinear) input/output
    systems to be represented in Python.  It is intended as a parent
    class for a set of subclasses that are used to implement specific
    structures and operations for different types of input/output
    dynamical systems.

    Parameters
    ----------
    inputs : int, list of str, or None
        Description of the system inputs.  This can be given as an integer
        count or as a list of strings that name the individual signals.  If an
        integer count is specified, the names of the signal will be of the
        form `s[i]` (where `s` is one of `u`, `y`, or `x`).  If this parameter
        is not given or given as `None`, the relevant quantity will be
        determined when possible based on other information provided to
        functions using the system.
    outputs : int, list of str, or None
        Description of the system outputs.  Same format as `inputs`.
    states : int, list of str, or None
        Description of the system states.  Same format as `inputs`.
    dt : None, True or float, optional
        System timebase. 0 (default) indicates continuous
        time, True indicates discrete time with unspecified sampling
        time, positive number is discrete time with specified
        sampling time, None indicates unspecified timebase (either
        continuous or discrete time).
    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.
    name : string, optional
        System name (used for specifying signals). If unspecified, a generic
        name <sys[id]> is generated with a unique integer id.

    Attributes
    ----------
    ninputs, noutputs, nstates : int
        Number of input, output and state variables
    input_index, output_index, state_index : dict
        Dictionary of signal names for the inputs, outputs and states and the
        index of the corresponding array
    dt : None, True or float
        System timebase. 0 (default) indicates continuous time, True indicates
        discrete time with unspecified sampling time, positive number is
        discrete time with specified sampling time, None indicates unspecified
        timebase (either continuous or discrete time).
    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.
    name : string, optional
        System name (used for specifying signals)

    Notes
    -----
    The :class:`~control.InputOuputSystem` class (and its subclasses) makes
    use of two special methods for implementing much of the work of the class:

    * _rhs(t, x, u): compute the right hand side of the differential or
      difference equation for the system.  This must be specified by the
      subclass for the system.

    * _out(t, x, u): compute the output for the current state of the system.
      The default is to return the entire system state.

    """

    # Allow ndarray * InputOutputSystem to give IOSystem._rmul_() priority
    __array_priority__ = 12     # override ndarray, matrix, SS types

    _idCounter = 0

    def _name_or_default(self, name=None):
        if name is None:
            name = "sys[{}]".format(InputOutputSystem._idCounter)
            InputOutputSystem._idCounter += 1
        return name

    def __init__(self, inputs=None, outputs=None, states=None, params={},
                 name=None, **kwargs):
        """Create an input/output system.

        The InputOutputSystem constructor is used to create an input/output
        object with the core information required for all input/output
        systems.  Instances of this class are normally created by one of the
        input/output subclasses: :class:`~control.LinearICSystem`,
        :class:`~control.LinearIOSystem`, :class:`~control.NonlinearIOSystem`,
        :class:`~control.InterconnectedSystem`.

        """
        # Store the input arguments

        # default parameters
        self.params = params.copy()
        # timebase
        self.dt = kwargs.get('dt', config.defaults['control.default_dt'])
        # system name
        self.name = self._name_or_default(name)

        # Parse and store the number of inputs, outputs, and states
        self.set_inputs(inputs)
        self.set_outputs(outputs)
        self.set_states(states)

    #
    # Class attributes
    #
    # These attributes are defined as class attributes so that they are
    # documented properly.  They are "overwritten" in __init__.
    #

    #: Number of system inputs.
    #:
    #: :meta hide-value:
    ninputs = 0

    #: Number of system outputs.
    #:
    #: :meta hide-value:
    noutputs = 0

    #: Number of system states.
    #:
    #: :meta hide-value:
    nstates = 0

    def __repr__(self):
        return self.name if self.name is not None else str(type(self))

    def __str__(self):
        """String representation of an input/output system"""
        str = "System: " + (self.name if self.name else "(None)") + "\n"
        str += "Inputs (%s): " % self.ninputs
        for key in self.input_index:
            str += key + ", "
        str += "\nOutputs (%s): " % self.noutputs
        for key in self.output_index:
            str += key + ", "
        str += "\nStates (%s): " % self.nstates
        for key in self.state_index:
            str += key + ", "
        return str

    def __mul__(sys2, sys1):
        """Multiply two input/output systems (series interconnection)"""
        # Note: order of arguments is flipped so that self = sys2,
        # corresponding to the ordering convention of sys2 * sys1

        # Convert sys1 to an I/O system if needed
        if isinstance(sys1, (int, float, np.number)):
            sys1 = LinearIOSystem(StateSpace(
                [], [], [], sys1 * np.eye(sys2.ninputs)))

        elif isinstance(sys1, np.ndarray):
            sys1 = LinearIOSystem(StateSpace([], [], [], sys1))

        elif isinstance(sys1, (StateSpace, TransferFunction)):
            sys1 = LinearIOSystem(sys1)

        elif not isinstance(sys1, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys1)

        # Make sure systems can be interconnected
        if sys1.noutputs != sys2.ninputs:
            raise ValueError("Can't multiply systems with incompatible "
                             "inputs and outputs")

        # Make sure timebase are compatible
        dt = common_timebase(sys1.dt, sys2.dt)

        # Create a new system to handle the composition
        inplist = [(0, i) for i in range(sys1.ninputs)]
        outlist = [(1, i) for i in range(sys2.noutputs)]
        newsys = InterconnectedSystem(
            (sys1, sys2), inplist=inplist, outlist=outlist)

        # Set up the connection map manually
        newsys.set_connect_map(np.block(
            [[np.zeros((sys1.ninputs, sys1.noutputs)),
              np.zeros((sys1.ninputs, sys2.noutputs))],
             [np.eye(sys2.ninputs, sys1.noutputs),
              np.zeros((sys2.ninputs, sys2.noutputs))]]
        ))

        # If both systems are linear, create LinearICSystem
        if isinstance(sys1, StateSpace) and isinstance(sys2, StateSpace):
            ss_sys = StateSpace.__mul__(sys2, sys1)
            return LinearICSystem(newsys, ss_sys)

        # Return the newly created InterconnectedSystem
        return newsys

    def __rmul__(sys1, sys2):
        """Pre-multiply an input/output systems by a scalar/matrix"""
        # Convert sys2 to an I/O system if needed
        if isinstance(sys2, (int, float, np.number)):
            sys2 = LinearIOSystem(StateSpace(
                [], [], [], sys2 * np.eye(sys1.noutputs)))

        elif isinstance(sys2, np.ndarray):
            sys2 = LinearIOSystem(StateSpace([], [], [], sys2))

        elif isinstance(sys2, (StateSpace, TransferFunction)):
            sys2 = LinearIOSystem(sys2)

        elif not isinstance(sys2, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys2)

        return InputOutputSystem.__mul__(sys2, sys1)

    def __add__(sys1, sys2):
        """Add two input/output systems (parallel interconnection)"""
        # Convert sys1 to an I/O system if needed
        if isinstance(sys2, (int, float, np.number)):
            sys2 = LinearIOSystem(StateSpace(
                [], [], [], sys2 * np.eye(sys1.ninputs)))

        elif isinstance(sys2, np.ndarray):
            sys2 = LinearIOSystem(StateSpace([], [], [], sys2))

        elif isinstance(sys2, (StateSpace, TransferFunction)):
            sys2 = LinearIOSystem(sys2)

        elif not isinstance(sys2, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys2)

        # Make sure number of input and outputs match
        if sys1.ninputs != sys2.ninputs or sys1.noutputs != sys2.noutputs:
            raise ValueError("Can't add systems with incompatible numbers of "
                             "inputs or outputs.")
        ninputs = sys1.ninputs
        noutputs = sys1.noutputs

        # Create a new system to handle the composition
        inplist = [[(0, i), (1, i)] for i in range(ninputs)]
        outlist = [[(0, i), (1, i)] for i in range(noutputs)]
        newsys = InterconnectedSystem(
            (sys1, sys2), inplist=inplist, outlist=outlist)

        # If both systems are linear, create LinearICSystem
        if isinstance(sys1, StateSpace) and isinstance(sys2, StateSpace):
            ss_sys = StateSpace.__add__(sys2, sys1)
            return LinearICSystem(newsys, ss_sys)

        # Return the newly created InterconnectedSystem
        return newsys

    def __radd__(sys1, sys2):
        """Parallel addition of input/output system to a compatible object."""
        # Convert sys2 to an I/O system if needed
        if isinstance(sys2, (int, float, np.number)):
            sys2 = LinearIOSystem(StateSpace(
                [], [], [], sys2 * np.eye(sys1.noutputs)))

        elif isinstance(sys2, np.ndarray):
            sys2 = LinearIOSystem(StateSpace([], [], [], sys2))

        elif isinstance(sys2, (StateSpace, TransferFunction)):
            sys2 = LinearIOSystem(sys2)

        elif not isinstance(sys2, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys2)

        return InputOutputSystem.__add__(sys2, sys1)

    def __sub__(sys1, sys2):
        """Subtract two input/output systems (parallel interconnection)"""
        # Convert sys1 to an I/O system if needed
        if isinstance(sys2, (int, float, np.number)):
            sys2 = LinearIOSystem(StateSpace(
                [], [], [], sys2 * np.eye(sys1.ninputs)))

        elif isinstance(sys2, np.ndarray):
            sys2 = LinearIOSystem(StateSpace([], [], [], sys2))

        elif isinstance(sys2, (StateSpace, TransferFunction)):
            sys2 = LinearIOSystem(sys2)

        elif not isinstance(sys2, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys2)

        # Make sure number of input and outputs match
        if sys1.ninputs != sys2.ninputs or sys1.noutputs != sys2.noutputs:
            raise ValueError("Can't add systems with incompatible numbers of "
                             "inputs or outputs.")
        ninputs = sys1.ninputs
        noutputs = sys1.noutputs

        # Create a new system to handle the composition
        inplist = [[(0, i), (1, i)] for i in range(ninputs)]
        outlist = [[(0, i), (1, i, -1)] for i in range(noutputs)]
        newsys = InterconnectedSystem(
            (sys1, sys2), inplist=inplist, outlist=outlist)

        # If both systems are linear, create LinearICSystem
        if isinstance(sys1, StateSpace) and isinstance(sys2, StateSpace):
            ss_sys = StateSpace.__sub__(sys1, sys2)
            return LinearICSystem(newsys, ss_sys)

        # Return the newly created InterconnectedSystem
        return newsys

    def __rsub__(sys1, sys2):
        """Parallel subtraction of I/O system to a compatible object."""
        # Convert sys2 to an I/O system if needed
        if isinstance(sys2, (int, float, np.number)):
            sys2 = LinearIOSystem(StateSpace(
                [], [], [], sys2 * np.eye(sys1.noutputs)))

        elif isinstance(sys2, np.ndarray):
            sys2 = LinearIOSystem(StateSpace([], [], [], sys2))

        elif isinstance(sys2, (StateSpace, TransferFunction)):
            sys2 = LinearIOSystem(sys2)

        elif not isinstance(sys2, InputOutputSystem):
            raise TypeError("Unknown I/O system object ", sys2)

        return InputOutputSystem.__sub__(sys2, sys1)

    def __neg__(sys):
        """Negate an input/output systems (rescale)"""
        if sys.ninputs is None or sys.noutputs is None:
            raise ValueError("Can't determine number of inputs or outputs")

        # Create a new system to hold the negation
        inplist = [(0, i) for i in range(sys.ninputs)]
        outlist = [(0, i, -1) for i in range(sys.noutputs)]
        newsys = InterconnectedSystem(
            (sys,), dt=sys.dt, inplist=inplist, outlist=outlist)

        # If the system is linear, create LinearICSystem
        if isinstance(sys, StateSpace):
            ss_sys = StateSpace.__neg__(sys)
            return LinearICSystem(newsys, ss_sys)

        # Return the newly created system
        return newsys

    def _isstatic(self):
        """Check to see if a system is a static system (no states)"""
        return self.nstates == 0

    # Utility function to parse a list of signals
    def _process_signal_list(self, signals, prefix='s'):
        if signals is None:
            # No information provided; try and make it up later
            return None, {}

        elif isinstance(signals, int):
            # Number of signals given; make up the names
            return signals, {'%s[%d]' % (prefix, i): i for i in range(signals)}

        elif isinstance(signals, str):
            # Single string given => single signal with given name
            return 1, {signals: 0}

        elif all(isinstance(s, str) for s in signals):
            # Use the list of strings as the signal names
            return len(signals), {signals[i]: i for i in range(len(signals))}

        else:
            raise TypeError("Can't parse signal list %s" % str(signals))

    # Find a signal by name
    def _find_signal(self, name, sigdict): return sigdict.get(name, None)

    # Update parameters used for _rhs, _out (used by subclasses)
    def _update_params(self, params, warning=False):
        if warning:
            warn("Parameters passed to InputOutputSystem ignored.")

    def _rhs(self, t, x, u, params={}):
        """Evaluate right hand side of a differential or difference equation.

        Private function used to compute the right hand side of an
        input/output system model. Intended for fast
        evaluation; for a more user-friendly interface
        you may want to use :meth:`dynamics`.

        """
        NotImplemented("Evaluation not implemented for system of type ",
                       type(self))

    def dynamics(self, t, x, u):
        """Compute the dynamics of a differential or difference equation.

        Given time `t`, input `u` and state `x`, returns the value of the
        right hand side of the dynamical system. If the system is continuous,
        returns the time derivative

            dx/dt = f(t, x, u)

        where `f` is the system's (possibly nonlinear) dynamics function.
        If the system is discrete-time, returns the next value of `x`:

            x[t+dt] = f(t, x[t], u[t])

        Where `t` is a scalar.

        The inputs `x` and `u` must be of the correct length.

        Parameters
        ----------
        t : float
            the time at which to evaluate
        x : array_like
            current state
        u : array_like
            input

        Returns
        -------
        dx/dt or x[t+dt] : ndarray
        """
        return self._rhs(t, x, u)

    def _out(self, t, x, u, params={}):
        """Evaluate the output of a system at a given state, input, and time

        Private function used to compute the output of of an input/output
        system model given the state, input, parameters. Intended for fast
        evaluation; for a more user-friendly interface you may want to use
        :meth:`output`.

        """
        # If no output function was defined in subclass, return state
        return x

    def output(self, t, x, u):
        """Compute the output of the system

        Given time `t`, input `u` and state `x`, returns the output of the
        system:

            y = g(t, x, u)

        The inputs `x` and `u` must be of the correct length.

        Parameters
        ----------
        t : float
            the time at which to evaluate
        x : array_like
            current state
        u : array_like
            input

        Returns
        -------
        y : ndarray
        """
        return self._out(t, x, u)

    def set_inputs(self, inputs, prefix='u'):
        """Set the number/names of the system inputs.

        Parameters
        ----------
        inputs : int, list of str, or None
            Description of the system inputs.  This can be given as an integer
            count or as a list of strings that name the individual signals.
            If an integer count is specified, the names of the signal will be
            of the form `u[i]` (where the prefix `u` can be changed using the
            optional prefix parameter).
        prefix : string, optional
            If `inputs` is an integer, create the names of the states using
            the given prefix (default = 'u').  The names of the input will be
            of the form `prefix[i]`.

        """
        self.ninputs, self.input_index = \
            self._process_signal_list(inputs, prefix=prefix)

    def set_outputs(self, outputs, prefix='y'):
        """Set the number/names of the system outputs.

        Parameters
        ----------
        outputs : int, list of str, or None
            Description of the system outputs.  This can be given as an integer
            count or as a list of strings that name the individual signals.
            If an integer count is specified, the names of the signal will be
            of the form `u[i]` (where the prefix `u` can be changed using the
            optional prefix parameter).
        prefix : string, optional
            If `outputs` is an integer, create the names of the states using
            the given prefix (default = 'y').  The names of the input will be
            of the form `prefix[i]`.

        """
        self.noutputs, self.output_index = \
            self._process_signal_list(outputs, prefix=prefix)

    def set_states(self, states, prefix='x'):
        """Set the number/names of the system states.

        Parameters
        ----------
        states : int, list of str, or None
            Description of the system states.  This can be given as an integer
            count or as a list of strings that name the individual signals.
            If an integer count is specified, the names of the signal will be
            of the form `u[i]` (where the prefix `u` can be changed using the
            optional prefix parameter).
        prefix : string, optional
            If `states` is an integer, create the names of the states using
            the given prefix (default = 'x').  The names of the input will be
            of the form `prefix[i]`.

        """
        self.nstates, self.state_index = \
            self._process_signal_list(states, prefix=prefix)

    def find_input(self, name):
        """Find the index for an input given its name (`None` if not found)"""
        return self.input_index.get(name, None)

    def find_output(self, name):
        """Find the index for an output given its name (`None` if not found)"""
        return self.output_index.get(name, None)

    def find_state(self, name):
        """Find the index for a state given its name (`None` if not found)"""
        return self.state_index.get(name, None)

    def issiso(self):
        """Check to see if a system is single input, single output"""
        return self.ninputs == 1 and self.noutputs == 1

    def feedback(self, other=1, sign=-1, params={}):
        """Feedback interconnection between two input/output systems

        Parameters
        ----------
        sys1: InputOutputSystem
            The primary process.
        sys2: InputOutputSystem
            The feedback process (often a feedback controller).
        sign: scalar, optional
            The sign of feedback.  `sign` = -1 indicates negative feedback,
            and `sign` = 1 indicates positive feedback.  `sign` is an optional
            argument; it assumes a value of -1 if not specified.

        Returns
        -------
        out: InputOutputSystem

        Raises
        ------
        ValueError
            if the inputs, outputs, or timebases of the systems are
            incompatible.

        """
        # TODO: add conversion to I/O system when needed
        if not isinstance(other, InputOutputSystem):
            # Try converting to a state space system
            try:
                other = _convert_to_statespace(other)
            except TypeError:
                raise TypeError(
                    "Feedback around I/O system must be an I/O system "
                    "or convertable to an I/O system.")
            other = LinearIOSystem(other)

        # Make sure systems can be interconnected
        if self.noutputs != other.ninputs or other.noutputs != self.ninputs:
            raise ValueError("Can't connect systems with incompatible "
                             "inputs and outputs")

        # Make sure timebases are compatible
        dt = common_timebase(self.dt, other.dt)

        inplist = [(0, i) for i in range(self.ninputs)]
        outlist = [(0, i) for i in range(self.noutputs)]

        # Return the series interconnection between the systems
        newsys = InterconnectedSystem(
            (self, other), inplist=inplist, outlist=outlist,
            params=params, dt=dt)

        #  Set up the connecton map manually
        newsys.set_connect_map(np.block(
            [[np.zeros((self.ninputs, self.noutputs)),
              sign * np.eye(self.ninputs, other.noutputs)],
             [np.eye(other.ninputs, self.noutputs),
              np.zeros((other.ninputs, other.noutputs))]]
        ))

        if isinstance(self, StateSpace) and isinstance(other, StateSpace):
            # Special case: maintain linear systems structure
            ss_sys = StateSpace.feedback(self, other, sign=sign)
            return LinearICSystem(newsys, ss_sys)

        # Return the newly created system
        return newsys

    def linearize(self, x0, u0, t=0, params={}, eps=1e-6,
                  name=None, copy=False, **kwargs):
        """Linearize an input/output system at a given state and input.

        Return the linearization of an input/output system at a given state
        and input value as a StateSpace system.  See
        :func:`~control.linearize` for complete documentation.

        """
        #
        # If the linearization is not defined by the subclass, perform a
        # numerical linearization use the `_rhs()` and `_out()` member
        # functions.
        #

        # Figure out dimensions if they were not specified.
        nstates = _find_size(self.nstates, x0)
        ninputs = _find_size(self.ninputs, u0)

        # Convert x0, u0 to arrays, if needed
        if np.isscalar(x0):
            x0 = np.ones((nstates,)) * x0
        if np.isscalar(u0):
            u0 = np.ones((ninputs,)) * u0

        # Compute number of outputs by evaluating the output function
        noutputs = _find_size(self.noutputs, self._out(t, x0, u0))

        # Update the current parameters
        self._update_params(params)

        # Compute the nominal value of the update law and output
        F0 = self._rhs(t, x0, u0)
        H0 = self._out(t, x0, u0)

        # Create empty matrices that we can fill up with linearizations
        A = np.zeros((nstates, nstates))        # Dynamics matrix
        B = np.zeros((nstates, ninputs))        # Input matrix
        C = np.zeros((noutputs, nstates))       # Output matrix
        D = np.zeros((noutputs, ninputs))       # Direct term

        # Perturb each of the state variables and compute linearization
        for i in range(nstates):
            dx = np.zeros((nstates,))
            dx[i] = eps
            A[:, i] = (self._rhs(t, x0 + dx, u0) - F0) / eps
            C[:, i] = (self._out(t, x0 + dx, u0) - H0) / eps

        # Perturb each of the input variables and compute linearization
        for i in range(ninputs):
            du = np.zeros((ninputs,))
            du[i] = eps
            B[:, i] = (self._rhs(t, x0, u0 + du) - F0) / eps
            D[:, i] = (self._out(t, x0, u0 + du) - H0) / eps

        # Create the state space system
        linsys = LinearIOSystem(
            StateSpace(A, B, C, D, self.dt, remove_useless=False),
            name=name, **kwargs)

        # Set the names the system, inputs, outputs, and states
        if copy:
            if name is None:
                linsys.name = \
                    config.defaults['iosys.linearized_system_name_prefix'] + \
                    self.name + \
                    config.defaults['iosys.linearized_system_name_suffix']
            linsys.ninputs, linsys.input_index = self.ninputs, \
                self.input_index.copy()
            linsys.noutputs, linsys.output_index = \
                self.noutputs, self.output_index.copy()
            linsys.nstates, linsys.state_index = \
                self.nstates, self.state_index.copy()

        return linsys

    def copy(self, newname=None):
        """Make a copy of an input/output system."""
        dup_prefix = config.defaults['iosys.duplicate_system_name_prefix']
        dup_suffix = config.defaults['iosys.duplicate_system_name_suffix']
        newsys = copy.copy(self)
        newsys.name = self._name_or_default(
            dup_prefix + self.name + dup_suffix if not newname else newname)
        return newsys


class LinearIOSystem(InputOutputSystem, StateSpace):
    """Input/output representation of a linear (state space) system.

    This class is used to implement a system that is a linear state
    space system (defined by the StateSpace system object).

    Parameters
    ----------
    linsys : StateSpace or TransferFunction
        LTI system to be converted
    inputs : int, list of str or None, optional
        Description of the system inputs.  This can be given as an integer
        count or as a list of strings that name the individual signals.  If an
        integer count is specified, the names of the signal will be of the
        form `s[i]` (where `s` is one of `u`, `y`, or `x`).  If this parameter
        is not given or given as `None`, the relevant quantity will be
        determined when possible based on other information provided to
        functions using the system.
    outputs : int, list of str or None, optional
        Description of the system outputs.  Same format as `inputs`.
    states : int, list of str, or None, optional
        Description of the system states.  Same format as `inputs`.
    dt : None, True or float, optional
        System timebase. 0 (default) indicates continuous time, True indicates
        discrete time with unspecified sampling time, positive number is
        discrete time with specified sampling time, None indicates unspecified
        timebase (either continuous or discrete time).
    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.
    name : string, optional
        System name (used for specifying signals). If unspecified, a
        generic name <sys[id]> is generated with a unique integer id.

    Attributes
    ----------
    ninputs, noutputs, nstates, dt, etc
        See :class:`InputOutputSystem` for inherited attributes.

    A, B, C, D
        See :class:`~control.StateSpace` for inherited attributes.

    """
    def __init__(self, linsys, inputs=None, outputs=None, states=None,
                 name=None, **kwargs):
        """Create an I/O system from a state space linear system.

        Converts a :class:`~control.StateSpace` system into an
        :class:`~control.InputOutputSystem` with the same inputs, outputs, and
        states.  The new system can be a continuous or discrete time system.

        """
        if isinstance(linsys, TransferFunction):
            # Convert system to StateSpace
            linsys = _convert_to_statespace(linsys)

        elif not isinstance(linsys, StateSpace):
            raise TypeError("Linear I/O system must be a state space "
                            "or transfer function object")

        # Look for 'input' and 'output' parameter name variants
        inputs = _parse_signal_parameter(inputs, 'input', kwargs)
        outputs = _parse_signal_parameter(outputs, 'output', kwargs, end=True)

        # Create the I/O system object
        super(LinearIOSystem, self).__init__(
            inputs=linsys.ninputs, outputs=linsys.noutputs,
            states=linsys.nstates, params={}, dt=linsys.dt, name=name)

        # Initalize additional state space variables
        StateSpace.__init__(self, linsys, remove_useless=False)

        # Process input, output, state lists, if given
        # Make sure they match the size of the linear system
        ninputs, self.input_index = self._process_signal_list(
            inputs if inputs is not None else linsys.ninputs, prefix='u')
        if ninputs is not None and linsys.ninputs != ninputs:
            raise ValueError("Wrong number/type of inputs given.")
        noutputs, self.output_index = self._process_signal_list(
            outputs if outputs is not None else linsys.noutputs, prefix='y')
        if noutputs is not None and linsys.noutputs != noutputs:
            raise ValueError("Wrong number/type of outputs given.")
        nstates, self.state_index = self._process_signal_list(
            states if states is not None else linsys.nstates, prefix='x')
        if nstates is not None and linsys.nstates != nstates:
            raise ValueError("Wrong number/type of states given.")

    # The following text needs to be replicated from StateSpace in order for
    # this entry to show up properly in sphinx doccumentation (not sure why,
    # but it was the only way to get it to work).
    #
    #: Deprecated attribute; use :attr:`nstates` instead.
    #:
    #: The ``state`` attribute was used to store the number of states for : a
    #: state space system.  It is no longer used.  If you need to access the
    #: number of states, use :attr:`nstates`.
    states = property(StateSpace._get_states, StateSpace._set_states)

    def _update_params(self, params={}, warning=True):
        # Parameters not supported; issue a warning
        if params and warning:
            warn("Parameters passed to LinearIOSystems are ignored.")

    def _rhs(self, t, x, u):
        # Convert input to column vector and then change output to 1D array
        xdot = self.A @ np.reshape(x, (-1, 1)) \
               + self.B @ np.reshape(u, (-1, 1))
        return np.array(xdot).reshape((-1,))

    def _out(self, t, x, u):
        # Convert input to column vector and then change output to 1D array
        y = self.C @ np.reshape(x, (-1, 1)) \
            + self.D @ np.reshape(u, (-1, 1))
        return np.array(y).reshape((-1,))


class NonlinearIOSystem(InputOutputSystem):
    """Nonlinear I/O system.

    Creates an :class:`~control.InputOutputSystem` for a nonlinear system by
    specifying a state update function and an output function.  The new system
    can be a continuous or discrete time system (Note: discrete-time systems
    are not yet supported by most functions.)

    Parameters
    ----------
    updfcn : callable
        Function returning the state update function

            `updfcn(t, x, u, params) -> array`

        where `x` is a 1-D array with shape (nstates,), `u` is a 1-D array
        with shape (ninputs,), `t` is a float representing the currrent
        time, and `params` is a dict containing the values of parameters
        used by the function.

    outfcn : callable
        Function returning the output at the given state

            `outfcn(t, x, u, params) -> array`

        where the arguments are the same as for `upfcn`.

    inputs : int, list of str or None, optional
        Description of the system inputs.  This can be given as an integer
        count or as a list of strings that name the individual signals.
        If an integer count is specified, the names of the signal will be
        of the form `s[i]` (where `s` is one of `u`, `y`, or `x`).  If
        this parameter is not given or given as `None`, the relevant
        quantity will be determined when possible based on other
        information provided to functions using the system.

    outputs : int, list of str or None, optional
        Description of the system outputs.  Same format as `inputs`.

    states : int, list of str, or None, optional
        Description of the system states.  Same format as `inputs`.

    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation
        functions for the system as default values, overriding internal
        defaults.

    dt : timebase, optional
        The timebase for the system, used to specify whether the system is
        operating in continuous or discrete time.  It can have the
        following values:

        * dt = 0: continuous time system (default)
        * dt > 0: discrete time system with sampling period 'dt'
        * dt = True: discrete time with unspecified sampling period
        * dt = None: no timebase specified

    name : string, optional
        System name (used for specifying signals). If unspecified, a
        generic name <sys[id]> is generated with a unique integer id.

    """
    def __init__(self, updfcn, outfcn=None, inputs=None, outputs=None,
                 states=None, params={}, name=None, **kwargs):
        """Create a nonlinear I/O system given update and output functions."""
        # Look for 'input' and 'output' parameter name variants
        inputs = _parse_signal_parameter(inputs, 'input', kwargs)
        outputs = _parse_signal_parameter(outputs, 'output', kwargs)

        # Store the update and output functions
        self.updfcn = updfcn
        self.outfcn = outfcn

        # Initialize the rest of the structure
        dt = kwargs.pop('dt', config.defaults['control.default_dt'])
        super(NonlinearIOSystem, self).__init__(
            inputs=inputs, outputs=outputs, states=states,
            params=params, dt=dt, name=name
        )

        # Make sure all input arguments got parsed
        if kwargs:
            raise TypeError("unknown parameters %s" % kwargs)

        # Check to make sure arguments are consistent
        if updfcn is None:
            if self.nstates is None:
                self.nstates = 0
            else:
                raise ValueError("States specified but no update function "
                                 "given.")
        if outfcn is None:
            # No output function specified => outputs = states
            if self.noutputs is None and self.nstates is not None:
                self.noutputs = self.nstates
            elif self.noutputs is not None and self.noutputs == self.nstates:
                # Number of outputs = number of states => all is OK
                pass
            elif self.noutputs is not None and self.noutputs != 0:
                raise ValueError("Outputs specified but no output function "
                                 "(and nstates not known).")

        # Initialize current parameters to default parameters
        self._current_params = params.copy()

    # Return the value of a static nonlinear system
    def __call__(sys, u, params=None, squeeze=None):
        """Evaluate a (static) nonlinearity at a given input value

        If a nonlinear I/O system has no internal state, then evaluating the
        system at an input `u` gives the output `y = F(u)`, determined by the
        output function.

        Parameters
        ----------
        params : dict, optional
            Parameter values for the system. Passed to the evaluation function
            for the system as default values, overriding internal defaults.
        squeeze : bool, optional
            If True and if the system has a single output, return the system
            output as a 1D array rather than a 2D array.  If False, return the
            system output as a 2D array even if the system is SISO.  Default
            value set by config.defaults['control.squeeze_time_response'].

        """

        # Make sure the call makes sense
        if not sys._isstatic():
            raise TypeError(
                "function evaluation is only supported for static "
                "input/output systems")

        # If we received any parameters, update them before calling _out()
        if params is not None:
            sys._update_params(params)

        # Evaluate the function on the argument
        out = sys._out(0, np.array((0,)), np.asarray(u))
        _, out = _process_time_response(
            None, out, issiso=sys.issiso(), squeeze=squeeze)
        return out

    def _update_params(self, params, warning=False):
        # Update the current parameter values
        self._current_params = self.params.copy()
        self._current_params.update(params)

    def _rhs(self, t, x, u):
        xdot = self.updfcn(t, x, u, self._current_params) \
            if self.updfcn is not None else []
        return np.array(xdot).reshape((-1,))

    def _out(self, t, x, u):
        y = self.outfcn(t, x, u, self._current_params) \
            if self.outfcn is not None else x
        return np.array(y).reshape((-1,))


class InterconnectedSystem(InputOutputSystem):
    """Interconnection of a set of input/output systems.

    This class is used to implement a system that is an interconnection of
    input/output systems.  The sys consists of a collection of subsystems
    whose inputs and outputs are connected via a connection map.  The overall
    system inputs and outputs are subsets of the subsystem inputs and outputs.

    See :func:`~control.interconnect` for a list of parameters.

    """
    def __init__(self, syslist, connections=[], inplist=[], outlist=[],
                 inputs=None, outputs=None, states=None,
                 params={}, dt=None, name=None, **kwargs):
        """Create an I/O system from a list of systems + connection info."""

        # Look for 'input' and 'output' parameter name variants
        inputs = _parse_signal_parameter(inputs, 'input', kwargs)
        outputs =  _parse_signal_parameter(outputs, 'output', kwargs, end=True)

        # Convert input and output names to lists if they aren't already
        if not isinstance(inplist, (list, tuple)):
            inplist = [inplist]
        if not isinstance(outlist, (list, tuple)):
            outlist = [outlist]

        # Check to make sure all systems are consistent
        self.syslist = syslist
        self.syslist_index = {}
        nstates = 0
        self.state_offset = []
        ninputs = 0
        self.input_offset = []
        noutputs = 0
        self.output_offset = []
        sysobj_name_dct = {}
        sysname_count_dct = {}
        for sysidx, sys in enumerate(syslist):
            # Make sure time bases are consistent
            dt = common_timebase(dt, sys.dt)

            # Make sure number of inputs, outputs, states is given
            if sys.ninputs is None or sys.noutputs is None or \
               sys.nstates is None:
                raise TypeError("System '%s' must define number of inputs, "
                                "outputs, states in order to be connected" %
                                sys.name)

            # Keep track of the offsets into the states, inputs, outputs
            self.input_offset.append(ninputs)
            self.output_offset.append(noutputs)
            self.state_offset.append(nstates)

            # Keep track of the total number of states, inputs, outputs
            nstates += sys.nstates
            ninputs += sys.ninputs
            noutputs += sys.noutputs

            # Check for duplicate systems or duplicate names
            # Duplicates are renamed sysname_1, sysname_2, etc.
            if sys in sysobj_name_dct:
                sys = sys.copy()
                warn("Duplicate object found in system list: %s. "
                     "Making a copy" % str(sys.name))
            if sys.name is not None and sys.name in sysname_count_dct:
                count = sysname_count_dct[sys.name]
                sysname_count_dct[sys.name] += 1
                sysname = sys.name + "_" + str(count)
                sysobj_name_dct[sys] = sysname
                self.syslist_index[sysname] = sysidx
                warn("Duplicate name found in system list. "
                     "Renamed to {}".format(sysname))
            else:
                sysname_count_dct[sys.name] = 1
                sysobj_name_dct[sys] = sys.name
                self.syslist_index[sys.name] = sysidx

        if states is None:
            states = []
            state_name_delim = config.defaults['iosys.state_name_delim']
            for sys, sysname in sysobj_name_dct.items():
                states += [sysname + state_name_delim +
                           statename for statename in sys.state_index.keys()]

        # Create the I/O system
        super(InterconnectedSystem, self).__init__(
            inputs=len(inplist), outputs=len(outlist),
            states=states, params=params, dt=dt, name=name)

        # If input or output list was specified, update it
        if inputs is not None:
            nsignals, self.input_index = \
                self._process_signal_list(inputs, prefix='u')
            if nsignals is not None and len(inplist) != nsignals:
                raise ValueError("Wrong number/type of inputs given.")
        if outputs is not None:
            nsignals, self.output_index = \
                self._process_signal_list(outputs, prefix='y')
            if nsignals is not None and len(outlist) != nsignals:
                raise ValueError("Wrong number/type of outputs given.")

        # Convert the list of interconnections to a connection map (matrix)
        self.connect_map = np.zeros((ninputs, noutputs))
        for connection in connections:
            input_index = self._parse_input_spec(connection[0])
            for output_spec in connection[1:]:
                output_index, gain = self._parse_output_spec(output_spec)
                if self.connect_map[input_index, output_index] != 0:
                    warn("multiple connections given for input %d" %
                         input_index + ". Combining with previous entries.")
                self.connect_map[input_index, output_index] += gain

        # Convert the input list to a matrix: maps system to subsystems
        self.input_map = np.zeros((ninputs, self.ninputs))
        for index, inpspec in enumerate(inplist):
            if isinstance(inpspec, (int, str, tuple)):
                inpspec = [inpspec]
            if not isinstance(inpspec, list):
                raise ValueError("specifications in inplist must be of type "
                                 "int, str, tuple or list.")
            for spec in inpspec:
                ulist_index = self._parse_input_spec(spec)
                if self.input_map[ulist_index, index] != 0:
                    warn("multiple connections given for input %d" %
                         index + ". Combining with previous entries.")
                self.input_map[ulist_index, index] += 1

        # Convert the output list to a matrix: maps subsystems to system
        self.output_map = np.zeros((self.noutputs, noutputs + ninputs))
        for index, outspec in enumerate(outlist):
            if isinstance(outspec, (int, str, tuple)):
                outspec = [outspec]
            if not isinstance(outspec, list):
                raise ValueError("specifications in outlist must be of type "
                                 "int, str, tuple or list.")
            for spec in outspec:
                ylist_index, gain = self._parse_output_spec(spec)
                if self.output_map[index, ylist_index] != 0:
                    warn("multiple connections given for output %d" %
                         index + ". Combining with previous entries.")
                self.output_map[index, ylist_index] += gain

        # Save the parameters for the system
        self.params = params.copy()

    def _update_params(self, params, warning=False):
        for sys in self.syslist:
            local = sys.params.copy()   # start with system parameters
            local.update(self.params)   # update with global params
            local.update(params)        # update with locally passed parameters
            sys._update_params(local, warning=warning)

    def _rhs(self, t, x, u):
        # Make sure state and input are vectors
        x = np.array(x, ndmin=1)
        u = np.array(u, ndmin=1)

        # Compute the input and output vectors
        ulist, ylist = self._compute_static_io(t, x, u)

        # Go through each system and update the right hand side for that system
        xdot = np.zeros((self.nstates,))        # Array to hold results
        state_index, input_index = 0, 0         # Start at the beginning
        for sys in self.syslist:
            # Update the right hand side for this subsystem
            if sys.nstates != 0:
                xdot[state_index:state_index + sys.nstates] = sys._rhs(
                    t, x[state_index:state_index + sys.nstates],
                    ulist[input_index:input_index + sys.ninputs])

            # Update the state and input index counters
            state_index += sys.nstates
            input_index += sys.ninputs

        return xdot

    def _out(self, t, x, u):
        # Make sure state and input are vectors
        x = np.array(x, ndmin=1)
        u = np.array(u, ndmin=1)

        # Compute the input and output vectors
        ulist, ylist = self._compute_static_io(t, x, u)

        # Make the full set of subsystem outputs to system output
        return self.output_map @ ylist

    def _compute_static_io(self, t, x, u):
        # Figure out the total number of inputs and outputs
        (ninputs, noutputs) = self.connect_map.shape

        #
        # Get the outputs and inputs at the current system state
        #

        # Initialize the lists used to keep track of internal signals
        ulist = np.dot(self.input_map, u)
        ylist = np.zeros((noutputs + ninputs,))

        # To allow for feedthrough terms, iterate multiple times to allow
        # feedthrough elements to propagate.  For n systems, we could need to
        # cycle through n+1 times before reaching steady state
        # TODO (later): see if there is a more efficient way to compute
        cycle_count = len(self.syslist) + 1
        while cycle_count > 0:
            state_index, input_index, output_index = 0, 0, 0
            for sys in self.syslist:
                # Compute outputs for each system from current state
                ysys = sys._out(
                    t, x[state_index:state_index + sys.nstates],
                    ulist[input_index:input_index + sys.ninputs])

                # Store the outputs at the start of ylist
                ylist[output_index:output_index + sys.noutputs] = \
                    ysys.reshape((-1,))

                # Store the input in the second part of ylist
                ylist[noutputs + input_index:
                      noutputs + input_index + sys.ninputs] = \
                          ulist[input_index:input_index + sys.ninputs]

                # Increment the index pointers
                state_index += sys.nstates
                input_index += sys.ninputs
                output_index += sys.noutputs

            # Compute inputs based on connection map
            new_ulist = self.connect_map @ ylist[:noutputs] \
                + np.dot(self.input_map, u)

            # Check to see if any of the inputs changed
            if (ulist == new_ulist).all():
                break
            else:
                ulist = new_ulist

            # Decrease the cycle counter
            cycle_count -= 1

        # Make sure that we stopped before detecting an algebraic loop
        if cycle_count == 0:
            raise RuntimeError("Algebraic loop detected.")

        return ulist, ylist

    def _parse_input_spec(self, spec):
        """Parse an input specification and returns the index

        This function parses a specification of an input of an interconnected
        system component and returns the index of that input in the internal
        input vector.  Input specifications are of one of the following forms:

            i               first input for the ith system
            (i,)            first input for the ith system
            (i, j)          jth input for the ith system
            'sys.sig'       signal 'sig' in subsys 'sys'
            ('sys', 'sig')  signal 'sig' in subsys 'sys'

        The function returns an index into the input vector array and
        the gain to use for that input.

        """
        # Parse the signal that we received
        subsys_index, input_index, gain = self._parse_signal(spec, 'input')
        if gain != 1:
            raise ValueError("gain not allowed in spec '%s'." % str(spec))

        # Return the index into the input vector list (ylist)
        return self.input_offset[subsys_index] + input_index

    def _parse_output_spec(self, spec):
        """Parse an output specification and returns the index and gain

        This function parses a specification of an output of an
        interconnected system component and returns the index of that
        output in the internal output vector (ylist).  Output specifications
        are of one of the following forms:

            i                       first output for the ith system
            (i,)                    first output for the ith system
            (i, j)                  jth output for the ith system
            (i, j, gain)            jth output for the ith system with gain
            'sys.sig'               signal 'sig' in subsys 'sys'
            '-sys.sig'              signal 'sig' in subsys 'sys' with gain -1
            ('sys', 'sig', gain)    signal 'sig' in subsys 'sys' with gain

        If the gain is not specified, it is taken to be 1.  Numbered outputs
        must be chosen from the list of subsystem outputs, but named outputs
        can also be contained in the list of subsystem inputs.

        The function returns an index into the output vector array and
        the gain to use for that output.

        """
        # Parse the rest of the spec with standard signal parsing routine
        try:
            # Start by looking in the set of subsystem outputs
            subsys_index, output_index, gain = \
                self._parse_signal(spec, 'output')

            # Return the index into the input vector list (ylist)
            return self.output_offset[subsys_index] + output_index, gain

        except ValueError:
            # Try looking in the set of subsystem *inputs*
            subsys_index, input_index, gain = self._parse_signal(
                spec, 'input or output', dictname='input_index')

            # Return the index into the input vector list (ylist)
            noutputs = sum(sys.noutputs for sys in self.syslist)
            return noutputs + \
                self.input_offset[subsys_index] + input_index, gain

    def _parse_signal(self, spec, signame='input', dictname=None):
        """Parse a signal specification, returning system and signal index.

        Signal specifications are of one of the following forms:

            i               system_index = i, signal_index = 0
            (i,)            system_index = i, signal_index = 0
            (i, j)          system_index = i, signal_index = j
            'sys.sig'       signal 'sig' in subsys 'sys'
            ('sys', 'sig')  signal 'sig' in subsys 'sys'
            ('sys', j)      signal_index j in subsys 'sys'

        The function returns an index into the input vector array and
        the gain to use for that input.
        """
        import re

        gain = 1                # Default gain

        # Check for special forms of the input
        if isinstance(spec, tuple) and len(spec) == 3:
            gain = spec[2]
            spec = spec[:2]
        elif isinstance(spec, str) and spec[0] == '-':
            gain = -1
            spec = spec[1:]

        # Process cases where we are given indices as integers
        if isinstance(spec, int):
            return spec, 0, gain

        elif isinstance(spec, tuple) and len(spec) == 1 \
             and isinstance(spec[0], int):
            return spec[0], 0, gain

        elif isinstance(spec, tuple) and len(spec) == 2 \
             and all([isinstance(index, int) for index in spec]):
            return spec + (gain,)

        # Figure out the name of the dictionary to use
        if dictname is None:
            dictname = signame + '_index'

        if isinstance(spec, str):
            # If we got a dotted string, break up into pieces
            namelist = re.split(r'\.', spec)

            # For now, only allow signal level of system name
            # TODO: expand to allow nested signal names
            if len(namelist) != 2:
                raise ValueError("Couldn't parse %s signal reference '%s'."
                                 % (signame, spec))

            system_index = self._find_system(namelist[0])
            if system_index is None:
                raise ValueError("Couldn't find system '%s'." % namelist[0])

            signal_index = self.syslist[system_index]._find_signal(
                namelist[1], getattr(self.syslist[system_index], dictname))
            if signal_index is None:
                raise ValueError("Couldn't find %s signal '%s.%s'." %
                                 (signame, namelist[0], namelist[1]))

            return system_index, signal_index, gain

        # Handle the ('sys', 'sig'), (i, j), and mixed cases
        elif isinstance(spec, tuple) and len(spec) == 2 and \
             isinstance(spec[0], (str, int)) and \
             isinstance(spec[1], (str, int)):
            if isinstance(spec[0], int):
                system_index = spec[0]
                if system_index < 0 or system_index > len(self.syslist):
                    system_index = None
            else:
                system_index = self._find_system(spec[0])
            if system_index is None:
                raise ValueError("Couldn't find system '%s'." % spec[0])

            if isinstance(spec[1], int):
                signal_index = spec[1]
                # TODO (later): check against max length of appropriate list?
                if signal_index < 0:
                    system_index = None
            else:
                signal_index = self.syslist[system_index]._find_signal(
                    spec[1], getattr(self.syslist[system_index], dictname))
            if signal_index is None:
                raise ValueError("Couldn't find signal %s.%s." % tuple(spec))

            return system_index, signal_index, gain

        else:
            raise ValueError("Couldn't parse signal reference %s." % str(spec))

    def _find_system(self, name):
        return self.syslist_index.get(name, None)

    def set_connect_map(self, connect_map):
        """Set the connection map for an interconnected I/O system.

        Parameters
        ----------
        connect_map : 2D array
             Specify the matrix that will be used to multiply the vector of
             subsystem outputs to obtain the vector of subsystem inputs.

        """
        # Make sure the connection map is the right size
        if connect_map.shape != self.connect_map.shape:
            ValueError("Connection map is not the right shape")
        self.connect_map = connect_map

    def set_input_map(self, input_map):
        """Set the input map for an interconnected I/O system.

        Parameters
        ----------
        input_map : 2D array
             Specify the matrix that will be used to multiply the vector of
             system inputs to obtain the vector of subsystem inputs.  These
             values are added to the inputs specified in the connection map.

        """
        # Figure out the number of internal inputs
        ninputs = sum(sys.ninputs for sys in self.syslist)

        # Make sure the input map is the right size
        if input_map.shape[0] != ninputs:
            ValueError("Input map is not the right shape")
        self.input_map = input_map
        self.ninputs = input_map.shape[1]

    def set_output_map(self, output_map):
        """Set the output map for an interconnected I/O system.

        Parameters
        ----------
        output_map : 2D array
             Specify the matrix that will be used to multiply the vector of
             subsystem outputs to obtain the vector of system outputs.
        """
        # Figure out the number of internal inputs and outputs
        ninputs = sum(sys.ninputs for sys in self.syslist)
        noutputs = sum(sys.noutputs for sys in self.syslist)

        # Make sure the output map is the right size
        if output_map.shape[1] == noutputs:
            # For backward compatibility, add zeros to the end of the array
            output_map = np.concatenate(
                (output_map,
                 np.zeros((output_map.shape[0], ninputs))),
                axis=1)

        if output_map.shape[1] != noutputs + ninputs:
            ValueError("Output map is not the right shape")
        self.output_map = output_map
        self.noutputs = output_map.shape[0]

    def unused_signals(self):
        """Find unused subsystem inputs and outputs

        Returns
        -------

        unused_inputs : dict

          A mapping from tuple of indices (isys, isig) to string
          '{sys}.{sig}', for all unused subsystem inputs.

        unused_outputs : dict

          A mapping from tuple of indices (isys, isig) to string
          '{sys}.{sig}', for all unused subsystem outputs.

        """
        used_sysinp_via_inp = np.nonzero(self.input_map)[0]
        used_sysout_via_out = np.nonzero(self.output_map)[1]
        used_sysinp_via_con, used_sysout_via_con = np.nonzero(self.connect_map)

        used_sysinp = set(used_sysinp_via_inp) | set(used_sysinp_via_con)
        used_sysout = set(used_sysout_via_out) | set(used_sysout_via_con)

        nsubsysinp = sum(sys.ninputs for sys in self.syslist)
        nsubsysout = sum(sys.noutputs for sys in self.syslist)

        unused_sysinp = sorted(set(range(nsubsysinp)) - used_sysinp)
        unused_sysout = sorted(set(range(nsubsysout)) - used_sysout)

        inputs = [(isys, isig, f'{sys.name}.{sig}')
                  for isys, sys in enumerate(self.syslist)
                  for sig, isig in sys.input_index.items()]

        outputs = [(isys, isig, f'{sys.name}.{sig}')
                   for isys, sys in enumerate(self.syslist)
                   for sig, isig in sys.output_index.items()]

        return ({inputs[i][:2]: inputs[i][2] for i in unused_sysinp},
                {outputs[i][:2]: outputs[i][2] for i in unused_sysout})

    def _find_inputs_by_basename(self, basename):
        """Find all subsystem inputs matching basename

        Returns
        -------
        Mapping from (isys, isig) to '{sys}.{sig}'

        """
        return {(isys, isig): f'{sys.name}.{basename}'
                for isys, sys in enumerate(self.syslist)
                for sig, isig in sys.input_index.items()
                if sig == (basename)}

    def _find_outputs_by_basename(self, basename):
        """Find all subsystem outputs matching basename

        Returns
        -------
        Mapping from (isys, isig) to '{sys}.{sig}'

        """
        return {(isys, isig): f'{sys.name}.{basename}'
                for isys, sys in enumerate(self.syslist)
                for sig, isig in sys.output_index.items()
                if sig == (basename)}

    def check_unused_signals(self, ignore_inputs=None, ignore_outputs=None):
        """Check for unused subsystem inputs and outputs

        If any unused inputs or outputs are found, emit a warning.

        Parameters
        ----------
        ignore_inputs : list of input-spec
          Subsystem inputs known to be unused.  input-spec can be any of:
            'sig', 'sys.sig', (isys, isig), ('sys', isig)

          If the 'sig' form is used, all subsystem inputs with that
          name are considered ignored.

        ignore_outputs : list of output-spec
          Subsystem outputs known to be unused.  output-spec can be any of:
            'sig', 'sys.sig', (isys, isig), ('sys', isig)

          If the 'sig' form is used, all subsystem outputs with that
          name are considered ignored.

        """

        if ignore_inputs is None:
            ignore_inputs = []

        if ignore_outputs is None:
            ignore_outputs = []

        unused_inputs, unused_outputs = self.unused_signals()

        # (isys, isig) -> signal-spec
        ignore_input_map = {}
        for ignore_input in ignore_inputs:
            if isinstance(ignore_input, str) and '.' not in ignore_input:
                ignore_idxs = self._find_inputs_by_basename(ignore_input)
                if not ignore_idxs:
                    raise ValueError("Couldn't find ignored input "
                                     f"{ignore_input} in subsystems")
                ignore_input_map.update(ignore_idxs)
            else:
                ignore_input_map[self._parse_signal(
                    ignore_input, 'input')[:2]] = ignore_input

        # (isys, isig) -> signal-spec
        ignore_output_map = {}
        for ignore_output in ignore_outputs:
            if isinstance(ignore_output, str) and '.' not in ignore_output:
                ignore_found = self._find_outputs_by_basename(ignore_output)
                if not ignore_found:
                    raise ValueError("Couldn't find ignored output "
                                     f"{ignore_output} in subsystems")
                ignore_output_map.update(ignore_found)
            else:
                ignore_output_map[self._parse_signal(
                    ignore_output, 'output')[:2]] = ignore_output

        dropped_inputs = set(unused_inputs) - set(ignore_input_map)
        dropped_outputs = set(unused_outputs) - set(ignore_output_map)

        used_ignored_inputs = set(ignore_input_map) - set(unused_inputs)
        used_ignored_outputs = set(ignore_output_map) - set(unused_outputs)

        if dropped_inputs:
            msg = ('Unused input(s) in InterconnectedSystem: '
                   + '; '.join(f'{inp}={unused_inputs[inp]}'
                               for inp in dropped_inputs))
            warn(msg)

        if dropped_outputs:
            msg = ('Unused output(s) in InterconnectedSystem: '
                   + '; '.join(f'{out} : {unused_outputs[out]}'
                               for out in dropped_outputs))
            warn(msg)

        if used_ignored_inputs:
            msg = ('Input(s) specified as ignored is (are) used: '
                   + '; '.join(f'{inp} : {ignore_input_map[inp]}'
                               for inp in used_ignored_inputs))
            warn(msg)

        if used_ignored_outputs:
            msg = ('Output(s) specified as ignored is (are) used: '
                   + '; '.join(f'{out}={ignore_output_map[out]}'
                               for out in used_ignored_outputs))
            warn(msg)


class LinearICSystem(InterconnectedSystem, LinearIOSystem):

    """Interconnection of a set of linear input/output systems.

    This class is used to implement a system that is an interconnection of
    linear input/output systems.  It has all of the structure of an
    :class:`~control.InterconnectedSystem`, but also maintains the requirement
    elements of :class:`~control.LinearIOSystem`, including the
    :class:`StateSpace` class structure, allowing it to be passed to functions
    that expect a :class:`StateSpace` system.

    This class is usually generated using :func:`~control.interconnect` and
    not called directly

    """

    def __init__(self, io_sys, ss_sys=None):
        if not isinstance(io_sys, InterconnectedSystem):
            raise TypeError("First argument must be an interconnected system.")

        # Create the I/O system object
        InputOutputSystem.__init__(
            self, name=io_sys.name, params=io_sys.params)

        # Copy over the I/O systems attributes
        self.syslist = io_sys.syslist
        self.ninputs = io_sys.ninputs
        self.noutputs = io_sys.noutputs
        self.nstates = io_sys.nstates
        self.input_index = io_sys.input_index
        self.output_index = io_sys.output_index
        self.state_index = io_sys.state_index
        self.dt = io_sys.dt

        # Copy over the attributes from the interconnected system
        self.syslist_index = io_sys.syslist_index
        self.state_offset = io_sys.state_offset
        self.input_offset = io_sys.input_offset
        self.output_offset = io_sys.output_offset
        self.connect_map = io_sys.connect_map
        self.input_map = io_sys.input_map
        self.output_map = io_sys.output_map
        self.params = io_sys.params

        # If we didnt' get a state space system, linearize the full system
        # TODO: this could be replaced with a direct computation (someday)
        if ss_sys is None:
            ss_sys = self.linearize(0, 0)

        # Initialize the state space attributes
        if isinstance(ss_sys, StateSpace):
            # Make sure the dimension match
            if io_sys.ninputs != ss_sys.ninputs or \
               io_sys.noutputs != ss_sys.noutputs or \
               io_sys.nstates != ss_sys.nstates:
                raise ValueError("System dimensions for first and second "
                                 "arguments must match.")
            StateSpace.__init__(self, ss_sys, remove_useless=False)

        else:
            raise TypeError("Second argument must be a state space system.")

    # The following text needs to be replicated from StateSpace in order for
    # this entry to show up properly in sphinx doccumentation (not sure why,
    # but it was the only way to get it to work).
    #
    #: Deprecated attribute; use :attr:`nstates` instead.
    #:
    #: The ``state`` attribute was used to store the number of states for : a
    #: state space system.  It is no longer used.  If you need to access the
    #: number of states, use :attr:`nstates`.
    states = property(StateSpace._get_states, StateSpace._set_states)


def input_output_response(
        sys, T, U=0., X0=0, params={},
        transpose=False, return_x=False, squeeze=None,
        solve_ivp_kwargs={}, **kwargs):
    """Compute the output response of a system to a given input.

    Simulate a dynamical system with a given input and return its output
    and state values.

    Parameters
    ----------
    sys : InputOutputSystem
        Input/output system to simulate.

    T : array-like
        Time steps at which the input is defined; values must be evenly spaced.

    U : array-like or number, optional
        Input array giving input at each time `T` (default = 0).

    X0 : array-like or number, optional
        Initial condition (default = 0).

    return_x : bool, optional
        If True, return the state vector when assigning to a tuple (default =
        False).  See :func:`forced_response` for more details.
        If True, return the values of the state at each time (default = False).

    squeeze : bool, optional
        If True and if the system has a single output, return the system
        output as a 1D array rather than a 2D array.  If False, return the
        system output as a 2D array even if the system is SISO.  Default value
        set by config.defaults['control.squeeze_time_response'].

    Returns
    -------
    results : TimeResponseData
        Time response represented as a :class:`TimeResponseData` object
        containing the following properties:

        * time (array): Time values of the output.

        * outputs (array): Response of the system.  If the system is SISO and
          `squeeze` is not True, the array is 1D (indexed by time).  If the
          system is not SISO or `squeeze` is False, the array is 2D (indexed
          by output and time).

        * states (array): Time evolution of the state vector, represented as
          a 2D array indexed by state and time.

        * inputs (array): Input(s) to the system, indexed by input and time.

        The return value of the system can also be accessed by assigning the
        function to a tuple of length 2 (time, output) or of length 3 (time,
        output, state) if ``return_x`` is ``True``.  If the input/output
        system signals are named, these names will be used as labels for the
        time response.

    Other parameters
    ----------------
    solve_ivp_method : str, optional
        Set the method used by :func:`scipy.integrate.solve_ivp`.  Defaults
        to 'RK45'.
    solve_ivp_kwargs : str, optional
        Pass additional keywords to :func:`scipy.integrate.solve_ivp`.

    Raises
    ------
    TypeError
        If the system is not an input/output system.
    ValueError
        If time step does not match sampling time (for discrete time systems).

    """
    #
    # Process keyword arguments
    #

    # Allow method as an alternative to solve_ivp_method
    if kwargs.get('method', None):
        solve_ivp_kwargs['method'] = kwargs.pop('method')

    # Figure out the method to be used
    if kwargs.get('solve_ivp_method', None):
        if kwargs.get('method', None):
            raise ValueError("ivp_method specified more than once")
        solve_ivp_kwargs['method'] = kwargs['solve_ivp_method']

    # Set the default method to 'RK45'
    if solve_ivp_kwargs.get('method', None) is None:
        solve_ivp_kwargs['method'] = 'RK45'

    # Sanity checking on the input
    if not isinstance(sys, InputOutputSystem):
        raise TypeError("System of type ", type(sys), " not valid")

    # Compute the time interval and number of steps
    T0, Tf = T[0], T[-1]
    n_steps = len(T)

    # Check and convert the input, if needed
    # TODO: improve MIMO ninputs check (choose from U)
    if sys.ninputs is None or sys.ninputs == 1:
        legal_shapes = [(n_steps,), (1, n_steps)]
    else:
        legal_shapes = [(sys.ninputs, n_steps)]
    U = _check_convert_array(U, legal_shapes,
                             'Parameter ``U``: ', squeeze=False)

    # Check to make sure this is not a static function
    nstates = _find_size(sys.nstates, X0)
    if nstates == 0:
        # No states => map input to output
        u = U[0] if len(U.shape) == 1 else U[:, 0]
        y = np.zeros((np.shape(sys._out(T[0], X0, u))[0], len(T)))
        for i in range(len(T)):
            u = U[i] if len(U.shape) == 1 else U[:, i]
            y[:, i] = sys._out(T[i], [], u)
        return TimeResponseData(
            T, y, None, U, issiso=sys.issiso(),
            output_labels=sys.output_index, input_labels=sys.input_index,
            transpose=transpose, return_x=return_x, squeeze=squeeze)

    # create X0 if not given, test if X0 has correct shape
    X0 = _check_convert_array(X0, [(nstates,), (nstates, 1)],
                              'Parameter ``X0``: ', squeeze=True)

    # Update the parameter values
    sys._update_params(params)

    #
    # Define a function to evaluate the input at an arbitrary time
    #
    # This is equivalent to the function
    #
    #   ufun = sp.interpolate.interp1d(T, U, fill_value='extrapolate')
    #
    # but has a lot less overhead => simulation runs much faster
    def ufun(t):
        # Find the value of the index using linear interpolation
        # Use clip to allow for extrapolation if t is out of range
        idx = np.clip(np.searchsorted(T, t, side='left'), 1, len(T)-1)
        dt = (t - T[idx-1]) / (T[idx] - T[idx-1])
        return U[..., idx-1] * (1. - dt) + U[..., idx] * dt

    # Create a lambda function for the right hand side
    def ivp_rhs(t, x):
        return sys._rhs(t, x, ufun(t))

    # Perform the simulation
    if isctime(sys):
        if not hasattr(sp.integrate, 'solve_ivp'):
            raise NameError("scipy.integrate.solve_ivp not found; "
                            "use SciPy 1.0 or greater")
        soln = sp.integrate.solve_ivp(
            ivp_rhs, (T0, Tf), X0, t_eval=T,
            vectorized=False, **solve_ivp_kwargs)

        # Compute the output associated with the state (and use sys.out to
        # figure out the number of outputs just in case it wasn't specified)
        u = U[0] if len(U.shape) == 1 else U[:, 0]
        y = np.zeros((np.shape(sys._out(T[0], X0, u))[0], len(T)))
        for i in range(len(T)):
            u = U[i] if len(U.shape) == 1 else U[:, i]
            y[:, i] = sys._out(T[i], soln.y[:, i], u)

    elif isdtime(sys):
        # Make sure the time vector is uniformly spaced
        dt = T[1] - T[0]
        if not np.allclose(T[1:] - T[:-1], dt):
            raise ValueError("Parameter ``T``: time values must be "
                             "equally spaced.")

        # Make sure the sample time matches the given time
        if (sys.dt is not True):
            # Make sure that the time increment is a multiple of sampling time

            # TODO: add back functionality for undersampling
            # TODO: this test is brittle if dt =  sys.dt
            # First make sure that time increment is bigger than sampling time
            # if dt < sys.dt:
            #     raise ValueError("Time steps ``T`` must match sampling time")

            # Check to make sure sampling time matches time increments
            if not np.isclose(dt, sys.dt):
                raise ValueError("Time steps ``T`` must be equal to "
                                 "sampling time")

        # Compute the solution
        soln = sp.optimize.OptimizeResult()
        soln.t = T                      # Store the time vector directly
        x = [float(x0) for x0 in X0]    # State vector (store as floats)
        soln.y = []                     # Solution, following scipy convention
        y = []                          # System output
        for i in range(len(T)):
            # Store the current state and output
            soln.y.append(x)
            y.append(sys._out(T[i], x, ufun(T[i])))

            # Update the state for the next iteration
            x = sys._rhs(T[i], x, ufun(T[i]))

        # Convert output to numpy arrays
        soln.y = np.transpose(np.array(soln.y))
        y = np.transpose(np.array(y))

        # Mark solution as successful
        soln.success = True     # No way to fail

    else:                       # Neither ctime or dtime??
        raise TypeError("Can't determine system type")

    return TimeResponseData(
        soln.t, y, soln.y, U, issiso=sys.issiso(),
        output_labels=sys.output_index, input_labels=sys.input_index,
        state_labels=sys.state_index,
        transpose=transpose, return_x=return_x, squeeze=squeeze)


def find_eqpt(sys, x0, u0=[], y0=None, t=0, params={},
              iu=None, iy=None, ix=None, idx=None, dx0=None,
              return_y=False, return_result=False, **kw):
    """Find the equilibrium point for an input/output system.

    Returns the value of an equilibrium point given the initial state and
    either input value or desired output value for the equilibrium point.

    Parameters
    ----------
    x0 : list of initial state values
        Initial guess for the value of the state near the equilibrium point.
    u0 : list of input values, optional
        If `y0` is not specified, sets the equilibrium value of the input.  If
        `y0` is given, provides an initial guess for the value of the input.
        Can be omitted if the system does not have any inputs.
    y0 : list of output values, optional
        If specified, sets the desired values of the outputs at the
        equilibrium point.
    t : float, optional
        Evaluation time, for time-varying systems
    params : dict, optional
        Parameter values for the system.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.
    iu : list of input indices, optional
        If specified, only the inputs with the given indices will be fixed at
        the specified values in solving for an equilibrium point.  All other
        inputs will be varied.  Input indices can be listed in any order.
    iy : list of output indices, optional
        If specified, only the outputs with the given indices will be fixed at
        the specified values in solving for an equilibrium point.  All other
        outputs will be varied.  Output indices can be listed in any order.
    ix : list of state indices, optional
        If specified, states with the given indices will be fixed at the
        specified values in solving for an equilibrium point.  All other
        states will be varied.  State indices can be listed in any order.
    dx0 : list of update values, optional
        If specified, the value of update map must match the listed value
        instead of the default value of 0.
    idx : list of state indices, optional
        If specified, state updates with the given indices will have their
        update maps fixed at the values given in `dx0`.  All other update
        values will be ignored in solving for an equilibrium point.  State
        indices can be listed in any order.  By default, all updates will be
        fixed at `dx0` in searching for an equilibrium point.
    return_y : bool, optional
        If True, return the value of output at the equilibrium point.
    return_result : bool, optional
        If True, return the `result` option from the
        :func:`scipy.optimize.root` function used to compute the equilibrium
        point.

    Returns
    -------
    xeq : array of states
        Value of the states at the equilibrium point, or `None` if no
        equilibrium point was found and `return_result` was False.
    ueq : array of input values
        Value of the inputs at the equilibrium point, or `None` if no
        equilibrium point was found and `return_result` was False.
    yeq : array of output values, optional
        If `return_y` is True, returns the value of the outputs at the
        equilibrium point, or `None` if no equilibrium point was found and
        `return_result` was False.
    result : :class:`scipy.optimize.OptimizeResult`, optional
        If `return_result` is True, returns the `result` from the
        :func:`scipy.optimize.root` function.

    """
    from scipy.optimize import root

    # Figure out the number of states, inputs, and outputs
    nstates = _find_size(sys.nstates, x0)
    ninputs = _find_size(sys.ninputs, u0)
    noutputs = _find_size(sys.noutputs, y0)

    # Convert x0, u0, y0 to arrays, if needed
    if np.isscalar(x0):
        x0 = np.ones((nstates,)) * x0
    if np.isscalar(u0):
        u0 = np.ones((ninputs,)) * u0
    if np.isscalar(y0):
        y0 = np.ones((ninputs,)) * y0

    # Discrete-time not yet supported
    if isdtime(sys, strict=True):
        raise NotImplementedError(
            "Discrete time systems are not yet supported.")

    # Make sure the input arguments match the sizes of the system
    if len(x0) != nstates or \
       (u0 is not None and len(u0) != ninputs) or \
       (y0 is not None and len(y0) != noutputs) or \
       (dx0 is not None and len(dx0) != nstates):
        raise ValueError("Length of input arguments does not match system.")

    # Update the parameter values
    sys._update_params(params)

    # Decide what variables to minimize
    if all([x is None for x in (iu, iy, ix, idx)]):
        # Special cases: either inputs or outputs are constrained
        if y0 is None:
            # Take u0 as fixed and minimize over x
            # TODO: update to allow discrete time systems
            def ode_rhs(z): return sys._rhs(t, z, u0)
            result = root(ode_rhs, x0, **kw)
            z = (result.x, u0, sys._out(t, result.x, u0))
        else:
            # Take y0 as fixed and minimize over x and u
            def rootfun(z):
                # Split z into x and u
                x, u = np.split(z, [nstates])
                # TODO: update to allow discrete time systems
                return np.concatenate(
                    (sys._rhs(t, x, u), sys._out(t, x, u) - y0), axis=0)
            z0 = np.concatenate((x0, u0), axis=0)   # Put variables together
            result = root(rootfun, z0, **kw)        # Find the eq point
            x, u = np.split(result.x, [nstates])    # Split result back in two
            z = (x, u, sys._out(t, x, u))

    else:
        # General case: figure out what variables to constrain
        # Verify the indices we are using are all in range
        if iu is not None:
            iu = np.unique(iu)
            if any([not isinstance(x, int) for x in iu]) or \
               (len(iu) > 0 and (min(iu) < 0 or max(iu) >= ninputs)):
                assert ValueError("One or more input indices is invalid")
        else:
            iu = []

        if iy is not None:
            iy = np.unique(iy)
            if any([not isinstance(x, int) for x in iy]) or \
               min(iy) < 0 or max(iy) >= noutputs:
                assert ValueError("One or more output indices is invalid")
        else:
            iy = list(range(noutputs))

        if ix is not None:
            ix = np.unique(ix)
            if any([not isinstance(x, int) for x in ix]) or \
               min(ix) < 0 or max(ix) >= nstates:
                assert ValueError("One or more state indices is invalid")
        else:
            ix = []

        if idx is not None:
            idx = np.unique(idx)
            if any([not isinstance(x, int) for x in idx]) or \
               min(idx) < 0 or max(idx) >= nstates:
                assert ValueError("One or more deriv indices is invalid")
        else:
            idx = list(range(nstates))

        # Construct the index lists for mapping variables and constraints
        #
        # The mechanism by which we implement the root finding function is to
        # map the subset of variables we are searching over into the inputs
        # and states, and then return a function that represents the equations
        # we are trying to solve.
        #
        # To do this, we need to carry out the following operations:
        #
        # 1. Given the current values of the free variables (z), map them into
        #    the portions of the state and input vectors that are not fixed.
        #
        # 2. Compute the update and output maps for the input/output system
        #    and extract the subset of equations that should be equal to zero.
        #
        # We perform these functions by computing four sets of index lists:
        #
        # * state_vars: indices of states that are allowed to vary
        # * input_vars: indices of inputs that are allowed to vary
        # * deriv_vars: indices of derivatives that must be constrained
        # * output_vars: indices of outputs that must be constrained
        #
        # This index lists can all be precomputed based on the `iu`, `iy`,
        # `ix`, and `idx` lists that were passed as arguments to `find_eqpt`
        # and were processed above.

        # Get the states and inputs that were not listed as fixed
        state_vars = (range(nstates) if not len(ix)
                      else np.delete(np.array(range(nstates)), ix))
        input_vars = (range(ninputs) if not len(iu)
                      else np.delete(np.array(range(ninputs)), iu))

        # Set the outputs and derivs that will serve as constraints
        output_vars = np.array(iy)
        deriv_vars = np.array(idx)

        # Verify that the number of degrees of freedom all add up correctly
        num_freedoms = len(state_vars) + len(input_vars)
        num_constraints = len(output_vars) + len(deriv_vars)
        if num_constraints != num_freedoms:
            warn("Number of constraints (%d) does not match number of degrees "
                 "of freedom (%d).  Results may be meaningless." %
                 (num_constraints, num_freedoms))

        # Make copies of the state and input variables to avoid overwriting
        # and convert to floats (in case ints were used for initial conditions)
        x = np.array(x0, dtype=float)
        u = np.array(u0, dtype=float)
        dx0 = np.array(dx0, dtype=float) if dx0 is not None \
            else np.zeros(x.shape)

        # Keep track of the number of states in the set of free variables
        nstate_vars = len(state_vars)
        dtime = isdtime(sys, strict=True)

        def rootfun(z):
            # Map the vector of values into the states and inputs
            x[state_vars] = z[:nstate_vars]
            u[input_vars] = z[nstate_vars:]

            # Compute the update and output maps
            dx = sys._rhs(t, x, u) - dx0
            if dtime:
                dx -= x           # TODO: check
            dy = sys._out(t, x, u) - y0

            # Map the results into the constrained variables
            return np.concatenate((dx[deriv_vars], dy[output_vars]), axis=0)

        # Set the initial condition for the root finding algorithm
        z0 = np.concatenate((x[state_vars], u[input_vars]), axis=0)

        # Finally, call the root finding function
        result = root(rootfun, z0, **kw)

        # Extract out the results and insert into x and u
        x[state_vars] = result.x[:nstate_vars]
        u[input_vars] = result.x[nstate_vars:]
        z = (x, u, sys._out(t, x, u))

    # Return the result based on what the user wants and what we found
    if not return_y:
        z = z[0:2]              # Strip y from result if not desired
    if return_result:
        # Return whatever we got, along with the result dictionary
        return z + (result,)
    elif result.success:
        # Return the result of the optimization
        return z
    else:
        # Something went wrong, don't return anything
        return (None, None, None) if return_y else (None, None)


# Linearize an input/output system
def linearize(sys, xeq, ueq=[], t=0, params={}, **kw):
    """Linearize an input/output system at a given state and input.

    This function computes the linearization of an input/output system at a
    given state and input value and returns a :class:`~control.StateSpace`
    object.  The evaluation point need not be an equilibrium point.

    Parameters
    ----------
    sys : InputOutputSystem
        The system to be linearized
    xeq : array
        The state at which the linearization will be evaluated (does not need
        to be an equilibrium state).
    ueq : array
        The input at which the linearization will be evaluated (does not need
        to correspond to an equlibrium state).
    t : float, optional
        The time at which the linearization will be computed (for time-varying
        systems).
    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.
    copy : bool, Optional
        If `copy` is True, copy the names of the input signals, output signals,
        and states to the linearized system.  If `name` is not specified,
        the system name is set to the input system name with the string
        '_linearized' appended.
    name : string, optional
        Set the name of the linearized system.  If not specified and
        if `copy` is `False`, a generic name <sys[id]> is generated
        with a unique integer id.  If `copy` is `True`, the new system
        name is determined by adding the prefix and suffix strings in
        config.defaults['iosys.linearized_system_name_prefix'] and
        config.defaults['iosys.linearized_system_name_suffix'], with the
        default being to add the suffix '$linearized'.

    Returns
    -------
    ss_sys : LinearIOSystem
        The linearization of the system, as a :class:`~control.LinearIOSystem`
        object (which is also a :class:`~control.StateSpace` object.

    """
    if not isinstance(sys, InputOutputSystem):
        raise TypeError("Can only linearize InputOutputSystem types")
    return sys.linearize(xeq, ueq, t=t, params=params, **kw)


# Utility function to parse a signal parameter
def _parse_signal_parameter(value, name, kwargs, end=False):
    # Check kwargs for a variant of the parameter name
    if value is None and name in kwargs:
        value = kwargs.pop(name)

    if end and kwargs:
        raise TypeError("unknown parameters %s" % kwargs)
    return value


def _find_size(sysval, vecval):
    """Utility function to find the size of a system parameter

    If both parameters are not None, they must be consistent.
    """
    if hasattr(vecval, '__len__'):
        if sysval is not None and sysval != len(vecval):
            raise ValueError("Inconsistent information to determine size "
                             "of system component")
        return len(vecval)
    # None or 0, which is a valid value for "a (sysval, ) vector of zeros".
    if not vecval:
        return 0 if sysval is None else sysval
    elif sysval == 1:
        # (1, scalar) is also a valid combination from legacy code
        return 1
    raise ValueError("Can't determine size of system component.")


# Convert a state space system into an input/output system (wrapper)
def ss2io(*args, **kwargs):
    return LinearIOSystem(*args, **kwargs)
ss2io.__doc__ = LinearIOSystem.__init__.__doc__


# Convert a transfer function into an input/output system (wrapper)
def tf2io(*args, **kwargs):
    """Convert a transfer function into an I/O system"""
    # TODO: add remaining documentation
    # Convert the system to a state space system
    linsys = tf2ss(*args)

    # Now convert the state space system to an I/O system
    return LinearIOSystem(linsys, **kwargs)


# Function to create an interconnected system
def interconnect(syslist, connections=None, inplist=[], outlist=[],
                 inputs=None, outputs=None, states=None,
                 params={}, dt=None, name=None,
                 check_unused=True, ignore_inputs=None, ignore_outputs=None,
                 **kwargs):
    """Interconnect a set of input/output systems.

    This function creates a new system that is an interconnection of a set of
    input/output systems.  If all of the input systems are linear I/O systems
    (type :class:`~control.LinearIOSystem`) then the resulting system will be
    a linear interconnected I/O system (type :class:`~control.LinearICSystem`)
    with the appropriate inputs, outputs, and states.  Otherwise, an
    interconnected I/O system (type :class:`~control.InterconnectedSystem`)
    will be created.

    Parameters
    ----------
    syslist : list of InputOutputSystems
        The list of input/output systems to be connected

    connections : list of connections, optional
        Description of the internal connections between the subsystems:

            [connection1, connection2, ...]

        Each connection is itself a list that describes an input to one of the
        subsystems.  The entries are of the form:

            [input-spec, output-spec1, output-spec2, ...]

        The input-spec can be in a number of different forms.  The lowest
        level representation is a tuple of the form `(subsys_i, inp_j)` where
        `subsys_i` is the index into `syslist` and `inp_j` is the index into
        the input vector for the subsystem.  If `subsys_i` has a single input,
        then the subsystem index `subsys_i` can be listed as the input-spec.
        If systems and signals are given names, then the form 'sys.sig' or
        ('sys', 'sig') are also recognized.

        Similarly, each output-spec should describe an output signal from one
        of the subsystems.  The lowest level representation is a tuple of the
        form `(subsys_i, out_j, gain)`.  The input will be constructed by
        summing the listed outputs after multiplying by the gain term.  If the
        gain term is omitted, it is assumed to be 1.  If the system has a
        single output, then the subsystem index `subsys_i` can be listed as
        the input-spec.  If systems and signals are given names, then the form
        'sys.sig', ('sys', 'sig') or ('sys', 'sig', gain) are also recognized,
        and the special form '-sys.sig' can be used to specify a signal with
        gain -1.

        If omitted, the `interconnect` function will attempt to create the
        interconnection map by connecting all signals with the same base names
        (ignoring the system name).  Specifically, for each input signal name
        in the list of systems, if that signal name corresponds to the output
        signal in any of the systems, it will be connected to that input (with
        a summation across all signals if the output name occurs in more than
        one system).

        The `connections` keyword can also be set to `False`, which will leave
        the connection map empty and it can be specified instead using the
        low-level :func:`~control.InterconnectedSystem.set_connect_map`
        method.

    inplist : list of input connections, optional
        List of connections for how the inputs for the overall system are
        mapped to the subsystem inputs.  The input specification is similar to
        the form defined in the connection specification, except that
        connections do not specify an input-spec, since these are the system
        inputs. The entries for a connection are thus of the form:

            [input-spec1, input-spec2, ...]

        Each system input is added to the input for the listed subsystem.  If
        the system input connects to only one subsystem input, a single input
        specification can be given (without the inner list).

        If omitted, the input map can be specified using the
        :func:`~control.InterconnectedSystem.set_input_map` method.

    outlist : list of output connections, optional
        List of connections for how the outputs from the subsystems are mapped
        to overall system outputs.  The output connection description is the
        same as the form defined in the inplist specification (including the
        optional gain term).  Numbered outputs must be chosen from the list of
        subsystem outputs, but named outputs can also be contained in the list
        of subsystem inputs.

        If an output connection contains more than one signal specification,
        then those signals are added together (multiplying by the any gain
        term) to form the system output.

        If omitted, the output map can be specified using the
        :func:`~control.InterconnectedSystem.set_output_map` method.

    inputs : int, list of str or None, optional
        Description of the system inputs.  This can be given as an integer
        count or as a list of strings that name the individual signals.  If an
        integer count is specified, the names of the signal will be of the
        form `s[i]` (where `s` is one of `u`, `y`, or `x`).  If this parameter
        is not given or given as `None`, the relevant quantity will be
        determined when possible based on other information provided to
        functions using the system.

    outputs : int, list of str or None, optional
        Description of the system outputs.  Same format as `inputs`.

    states : int, list of str, or None, optional
        Description of the system states.  Same format as `inputs`. The
        default is `None`, in which case the states will be given names of the
        form '<subsys_name>.<state_name>', for each subsys in syslist and each
        state_name of each subsys.

    params : dict, optional
        Parameter values for the systems.  Passed to the evaluation functions
        for the system as default values, overriding internal defaults.

    dt : timebase, optional
        The timebase for the system, used to specify whether the system is
        operating in continuous or discrete time.  It can have the following
        values:

        * dt = 0: continuous time system (default)
        * dt > 0: discrete time system with sampling period 'dt'
        * dt = True: discrete time with unspecified sampling period
        * dt = None: no timebase specified

    name : string, optional
        System name (used for specifying signals). If unspecified, a generic
        name <sys[id]> is generated with a unique integer id.

    check_unused : bool
        If True, check for unused sub-system signals.  This check is
        not done if connections is False, and neither input nor output
        mappings are specified.

    ignore_inputs : list of input-spec
        A list of sub-system inputs known not to be connected.  This is
        *only* used in checking for unused signals, and does not
        disable use of the input.

        Besides the usual input-spec forms (see `connections`), an
        input-spec can be just the signal base name, in which case all
        signals from all sub-systems with that base name are
        considered ignored.

    ignore_outputs : list of output-spec
        A list of sub-system outputs known not to be connected.  This
        is *only* used in checking for unused signals, and does not
        disable use of the output.

        Besides the usual output-spec forms (see `connections`), an
        output-spec can be just the signal base name, in which all
        outputs from all sub-systems with that base name are
        considered ignored.


    Example
    -------
    >>> P = control.LinearIOSystem(
    >>>        control.rss(2, 2, 2, strictly_proper=True), name='P')
    >>> C = control.LinearIOSystem(control.rss(2, 2, 2), name='C')
    >>> T = control.interconnect(
    >>>     [P, C],
    >>>     connections = [
    >>>       ['P.u[0]', 'C.y[0]'], ['P.u[1]', 'C.y[1]'],
    >>>       ['C.u[0]', '-P.y[0]'], ['C.u[1]', '-P.y[1]']],
    >>>     inplist = ['C.u[0]', 'C.u[1]'],
    >>>     outlist = ['P.y[0]', 'P.y[1]'],
    >>> )

    For a SISO system, this example can be simplified by using the
    :func:`~control.summing_block` function and the ability to automatically
    interconnect signals with the same names:

    >>> P = control.tf2io(control.tf(1, [1, 0]), inputs='u', outputs='y')
    >>> C = control.tf2io(control.tf(10, [1, 1]), inputs='e', outputs='u')
    >>> sumblk = control.summing_junction(inputs=['r', '-y'], output='e')
    >>> T = control.interconnect([P, C, sumblk], input='r', output='y')

    Notes
    -----
    If a system is duplicated in the list of systems to be connected,
    a warning is generated and a copy of the system is created with the
    name of the new system determined by adding the prefix and suffix
    strings in config.defaults['iosys.linearized_system_name_prefix']
    and config.defaults['iosys.linearized_system_name_suffix'], with the
    default being to add the suffix '$copy'$ to the system name.

    It is possible to replace lists in most of arguments with tuples instead,
    but strictly speaking the only use of tuples should be in the
    specification of an input- or output-signal via the tuple notation
    `(subsys_i, signal_j, gain)` (where `gain` is optional).  If you get an
    unexpected error message about a specification being of the wrong type,
    check your use of tuples.

    In addition to its use for general nonlinear I/O systems, the
    :func:`~control.interconnect` function allows linear systems to be
    interconnected using named signals (compared with the
    :func:`~control.connect` function, which uses signal indices) and to be
    treated as both a :class:`~control.StateSpace` system as well as an
    :class:`~control.InputOutputSystem`.

    The `input` and `output` keywords can be used instead of `inputs` and
    `outputs`, for more natural naming of SISO systems.

    """
    # Look for 'input' and 'output' parameter name variants
    inputs = _parse_signal_parameter(inputs, 'input', kwargs)
    outputs = _parse_signal_parameter(outputs, 'output', kwargs, end=True)

    if not check_unused and (ignore_inputs or ignore_outputs):
        raise ValueError('check_unused is False, but either '
                         + 'ignore_inputs or ignore_outputs non-empty')

    if (connections is False
        and not inplist and not outlist
        and not inputs and not outputs):
        # user has disabled auto-connect, and supplied neither input
        # nor output mappings; assume they know what they're doing
        check_unused = False

    # If connections was not specified, set up default connection list
    if connections is None:
        # For each system input, look for outputs with the same name
        connections = []
        for input_sys in syslist:
            for input_name in input_sys.input_index.keys():
                connect = [input_sys.name + "." + input_name]
                for output_sys in syslist:
                    if input_name in output_sys.output_index.keys():
                        connect.append(output_sys.name + "." + input_name)
                if len(connect) > 1:
                    connections.append(connect)

        auto_connect = True

    elif connections is False:
        check_unused = False
        # Use an empty connections list
        connections = []

    # If inplist/outlist is not present, try using inputs/outputs instead
    if not inplist and inputs is not None:
        inplist = list(inputs)
    if not outlist and outputs is not None:
        outlist = list(outputs)

    # Process input list
    if not isinstance(inplist, (list, tuple)):
        inplist = [inplist]
    new_inplist = []
    for signal in inplist:
        # Create an empty connection and append to inplist
        connection = []

        # Check for signal names without a system name
        if isinstance(signal, str) and len(signal.split('.')) == 1:
            # Get the signal name
            name = signal[1:] if signal[0] == '-' else signal
            sign = '-' if signal[0] == '-' else ""

            # Look for the signal name as a system input
            for sys in syslist:
                if name in sys.input_index.keys():
                    connection.append(sign + sys.name + "." + name)

            # Make sure we found the name
            if len(connection) == 0:
                raise ValueError("could not find signal %s" % name)
            else:
                new_inplist.append(connection)
        else:
            new_inplist.append(signal)
    inplist = new_inplist

    # Process output list
    if not isinstance(outlist, (list, tuple)):
        outlist = [outlist]
    new_outlist = []
    for signal in outlist:
        # Create an empty connection and append to inplist
        connection = []

        # Check for signal names without a system name
        if isinstance(signal, str) and len(signal.split('.')) == 1:
            # Get the signal name
            name = signal[1:] if signal[0] == '-' else signal
            sign = '-' if signal[0] == '-' else ""

            # Look for the signal name as a system output
            for sys in syslist:
                if name in sys.output_index.keys():
                    connection.append(sign + sys.name + "." + name)

            # Make sure we found the name
            if len(connection) == 0:
                raise ValueError("could not find signal %s" % name)
            else:
                new_outlist.append(connection)
        else:
            new_outlist.append(signal)
    outlist = new_outlist

    newsys = InterconnectedSystem(
        syslist, connections=connections, inplist=inplist, outlist=outlist,
        inputs=inputs, outputs=outputs, states=states,
        params=params, dt=dt, name=name)

    # check for implicity dropped signals
    if check_unused:
        newsys.check_unused_signals(ignore_inputs, ignore_outputs)
    # If all subsystems are linear systems, maintain linear structure
    if all([isinstance(sys, LinearIOSystem) for sys in syslist]):
        return LinearICSystem(newsys, None)

    return newsys


# Summing junction
def summing_junction(
        inputs=None, output=None, dimension=None, name=None,
        prefix='u', **kwargs):
    """Create a summing junction as an input/output system.

    This function creates a static input/output system that outputs the sum of
    the inputs, potentially with a change in sign for each individual input.
    The input/output system that is created by this function can be used as a
    component in the :func:`~control.interconnect` function.

    Parameters
    ----------
    inputs : int, string or list of strings
        Description of the inputs to the summing junction.  This can be given
        as an integer count, a string, or a list of strings. If an integer
        count is specified, the names of the input signals will be of the form
        `u[i]`.
    output : string, optional
        Name of the system output.  If not specified, the output will be 'y'.
    dimension : int, optional
        The dimension of the summing junction.  If the dimension is set to a
        positive integer, a multi-input, multi-output summing junction will be
        created.  The input and output signal names will be of the form
        `<signal>[i]` where `signal` is the input/output signal name specified
        by the `inputs` and `output` keywords.  Default value is `None`.
    name : string, optional
        System name (used for specifying signals). If unspecified, a generic
        name <sys[id]> is generated with a unique integer id.
    prefix : string, optional
        If `inputs` is an integer, create the names of the states using the
        given prefix (default = 'u').  The names of the input will be of the
        form `prefix[i]`.

    Returns
    -------
    sys : static LinearIOSystem
        Linear input/output system object with no states and only a direct
        term that implements the summing junction.

    Example
    -------
    >>> P = control.tf2io(ct.tf(1, [1, 0]), input='u', output='y')
    >>> C = control.tf2io(ct.tf(10, [1, 1]), input='e', output='u')
    >>> sumblk = control.summing_junction(inputs=['r', '-y'], output='e')
    >>> T = control.interconnect((P, C, sumblk), input='r', output='y')

    """
    # Utility function to parse input and output signal lists
    def _parse_list(signals, signame='input', prefix='u'):
        # Parse signals, including gains
        if isinstance(signals, int):
            nsignals = signals
            names = ["%s[%d]" % (prefix, i) for i in range(nsignals)]
            gains = np.ones((nsignals,))
        elif isinstance(signals, str):
            nsignals = 1
            gains = [-1 if signals[0] == '-' else 1]
            names = [signals[1:] if signals[0] == '-' else signals]
        elif isinstance(signals, list) and \
             all([isinstance(x, str) for x in signals]):
            nsignals = len(signals)
            gains = np.ones((nsignals,))
            names = []
            for i in range(nsignals):
                if signals[i][0] == '-':
                    gains[i] = -1
                    names.append(signals[i][1:])
                else:
                    names.append(signals[i])
        else:
            raise ValueError(
                "could not parse %s description '%s'"
                % (signame, str(signals)))

        # Return the parsed list
        return nsignals, names, gains

    # Look for 'input' and 'output' parameter name variants
    inputs = _parse_signal_parameter(inputs, 'input', kwargs)
    output = _parse_signal_parameter(output, 'outputs', kwargs, end=True)

    # Default values for inputs and output
    if inputs is None:
        raise TypeError("input specification is required")
    if output is None:
        output = 'y'

    # Read the input list
    ninputs, input_names, input_gains = _parse_list(
        inputs, signame="input", prefix=prefix)
    noutputs, output_names, output_gains = _parse_list(
        output, signame="output", prefix='y')
    if noutputs > 1:
        raise NotImplementedError("vector outputs not yet supported")

    # If the dimension keyword is present, vectorize inputs and outputs
    if isinstance(dimension, int) and dimension >= 1:
        # Create a new list of input/output names and update parameters
        input_names = ["%s[%d]" % (name, dim)
                       for name in input_names
                       for dim in range(dimension)]
        ninputs = ninputs * dimension

        output_names = ["%s[%d]" % (name, dim)
                        for name in output_names
                        for dim in range(dimension)]
        noutputs = noutputs * dimension
    elif dimension is not None:
        raise ValueError(
            "unrecognized dimension value '%s'" % str(dimension))
    else:
        dimension = 1

    # Create the direct term
    D = np.kron(input_gains * output_gains[0], np.eye(dimension))

    # Create a linear system of the appropriate size
    ss_sys = StateSpace(
        np.zeros((0, 0)), np.ones((0, ninputs)), np.ones((noutputs, 0)), D)

    # Create a LinearIOSystem
    return LinearIOSystem(
        ss_sys, inputs=input_names, outputs=output_names, name=name)

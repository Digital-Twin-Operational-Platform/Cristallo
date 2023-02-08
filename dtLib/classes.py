import numpy as np
from plotly.subplots import make_subplots
import json
import plotly
from scipy import signal, stats
import os


class TimeHistory():
    def __repr__(self):
        msg = f"Time history generated from {self.source}"
        return(msg)

    def __str__(self):
        msg = f"Time history generated from {self.source}"
        return(msg)

    def __init__(self, t=np.arange(0, 5, 1/10240), t_u: str = 'seconds', x=np.zeros(51200), x_u: str = 'g', source: str = 'Experiment'):
        self.time = t
        self.time_units = t_u
        self.response = x
        self.response_units = x_u
        self.source = source

    def plot(self):
        """
        Create a JSON plot file for the time history via Plotly
        """
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
        fig.add_scatter(x=self.time, y=self.response, mode='lines',
                        row=1, col=1, line={'color': 'black'})
        fig.update_xaxes(
            title_text=f"Time in {self.time_units}", titlefont=dict(size=15), row=1, col=1)
        fig.update_yaxes(title_text=f"Response in {self.response_units}", titlefont=dict(
            size=15), row=1, col=1)
        json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return(json_fig)  # Returns JSON figure file for DTOP

    def value(self, t=None):
        """
        Returns interpolated values at specified time
        """
        val = np.interp(t, self.time, self.response)
        return(val)

    def FFT(self):
        """
        Using generic Fast Fourier Transform, generates the frequency content of the time history
        """
        dt = self.time[1]-self.time[0]
        t = np.arange(self.time[0], self.time[-1], dt)
        y = self.value(t)
        resp = np.fft.fft(y)
        freq = np.fft.fftfreq(t.shape[-1], d=dt)
        resp, freq = resp[:int(len(resp)/2)], freq[:int(len(resp)/2)]
        self.fft_freq = freq
        self.fft_resp = resp

    def PSD(self):
        """
        Creates Power Spectral Density
        """
        try:
            self.psd_resp = (1/(2*len(self.fft_resp)**2)) * \
                np.abs(self.fft_resp)**2
            self.psd_freq = self.fft_freq
        except:
            self.FFT()
            self.psd_resp = (1/(2*len(self.fft_resp)**2)) * \
                np.abs(self.fft_resp)**2
            self.psd_freq = self.fft_freq

    def Hanning(self, size: float = 256):
        """
        If size is a decimal, takes int(floor(size)) as scaling size. Unknown units
        """
        dt = self.time[1]-self.time[0]
        t = np.arange(self.time[0], self.time[-1], dt)
        y = self.value(t)
        freq, Pxx = signal.welch(y, 1/dt, 'hann', size, scaling="spectrum")
        self.psd_freq = freq
        self.psd_resp = Pxx

    def plot_fft(self):
        """
        Checks to see if fft exists, then creates a JSON plot file for the FFT via Plotly
        """
        try:
            resp = np.abs(self.fft_resp)
            fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
            fig.add_scatter(x=self.fft_freq, y=resp, mode='lines',
                            row=1, col=1, line={'color': 'black'})
            fig.update_xaxes(title_text=f"Frequency in 1/{self.time_units}",
                             type="log", titlefont=dict(size=15), row=1, col=1)
            fig.update_yaxes(title_text=f"Magnitude of Response in |{self.response_units}|", titlefont=dict(
                size=15), row=1, col=1)
            json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return(json_fig)
        except:
            print("FFT is not generated, please generate FFT data")

    def plot_psd(self):
        """
        Checks to see if psd exists, then reates a JSON plot file for the PSD via Plotly
        """
        try:
            resp = self.psd_resp
            fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
            fig.add_scatter(x=self.psd_freq, y=resp, mode='lines',
                            row=1, col=1, line={'color': 'black'})
            fig.update_xaxes(title_text=f"Frequency in 1/{self.time_units}",
                             type="log", titlefont=dict(size=15), row=1, col=1)
            fig.update_yaxes(title_text=f"Power Spectral Density in {self.response_units}^2", titlefont=dict(
                size=15), row=1, col=1)
            json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return(json_fig)
        except:
            print("PSD is not generated, please generate PSD data")

class MODEL3DOF():
    def __repr__(self):  # return
        msg = f"3DOF model generated from {self.source}"
        return(msg)

    def __str__(self):  # Print
        msg = f"3DOF model generated from {self.source}"
        return(msg)

    def __init__(self, M=[5, 5, 5], mass_units: str = "kg", K=[40e3, 40e3, 40e3], stiff_units: str = "N/m", C=[6, 6, 6], damp_units: str = "Nm/s", dispersion=[0, 0, 0], dist:str = "normal", disp_units: str = "", source='user'):
        self.m1 = M[0]
        self.m2 = M[1]
        self.m3 = M[2]
        self.mass_units = mass_units
        self.k1 = K[0]
        self.k2 = K[1]
        self.k3 = K[2]
        self.stiff_units = stiff_units
        self.c1 = C[0]
        self.c2 = C[1]
        self.c3 = C[2]
        self.damp_units = damp_units
        self.disp_m = dispersion[0]
        self.disp_k = dispersion[1]
        self.disp_c = dispersion[2]
        self.disp_units = disp_units
        self.dist = dist
        self.source = source

    def matrix(self):  # return matrices
        """
        Generates 3x3 matrix representation of system. Output = M,K,C
        """
        M = np.array([[self.m1, 0, 0], [0, self.m2, 0], [self.m3, 0, 0]])
        K = np.array([[self.k1+self.k2, -self.k2, 0], [-self.k2,
                     self.k2+self.k3, -self.k3], [0, -self.k3, self.k3]])
        C = np.array([[self.c1+self.c2, -self.c2, 0], [-self.c2,
                     self.c2+self.c3, -self.c3], [0, -self.c3, self.c3]])
        return(M, K, C)

    def scalar(self):  # return scalar values
        """
        Returns scalar modular values, output = [m1,m2,m3], [k1,k2,k3], [c1,c2,c3]
        """
        M = [self.m1, self.m2, self.m3]
        K = [self.k1, self.k2, self.k3]
        C = [self.c1, self.c2, self.c3]
        return(M, K, C)

    def distribution(self):
        if self.dist == 'normal':
            m,k,c = self.scalar()
            M = stats.norm(loc=m, scale=3*[self.disp_m])
            K = stats.norm(loc=k, scale=3*[self.disp_k])
            C = stats.norm(loc=c, scale=3*[self.disp_c])
            return(M,K,C)
    def sample(self,N=10,seed=None):
        if seed is not None:
            np.random.seed(seed)
        M,K,C = self.distribution()
        return(M.rvs((N,3)),K.rvs((N,3)),C.rvs((N,3)))

    def toJSON(self, path=""):
        """
        Converts object to JSON format. If path is empty, returns to memory, 
        otherwise, saves to file
        """
        try:
            parse = path.rsplit('.', 1)[1]
        except:
            parse = path
        if parse == "":  # create json object to memory
            file = json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)
            return(file)
        elif path == "prompt":  # prompt user
            print("Enter in File Path")
            path = input()
            try:
                parse = path.rsplit('.', 1)[1]
            except:
                parse = path
            if  parse == "json":
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as fp:
                    json.dump(self, fp, default=lambda o: o.__dict__, indent=4, separators=",:")
            else:
                filename = os.path.join(path, "Model.json")
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w') as fp:
                    json.dump(self, fp, default=lambda o: o.__dict__, indent=4, separators=",:")
        elif parse == "json": # file is specified, write json to specified file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as fp:
                json.dump(self, fp, default=lambda o: o.__dict__, indent=4, separators=",:")
        else:  # file is not specified but folder is specified, create json file and write
            filename = os.path.join(path, "Model.json")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as fp:
                json.dump(self, fp, default=lambda o: o.__dict__, indent=4, separators=",:")

    def fromJSON(self, filepath=''):
        """
        Converts JSON file to 3DOF model
        """
        # Gather JSON file information
        if filepath == "":
            print("Enter in File Path")
            path = input()
            with open(path,'r') as fp:
                File = json.load(fp)
        else:
            with open(filepath,'r') as fp:
                File = json.load(fp)
        # Update Model from JSON
        keys = File.keys()
        for i in keys:
            setattr(self,i,File[i])

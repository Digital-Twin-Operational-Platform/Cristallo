import numpy as np
from plotly.subplots import make_subplots
import json
import plotly
import matplotlib.pyplot as plt
from scipy import signal


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
    """
    
    Break for Temperary Modules
    
    
    
    """

    def plot_pyplot(self):
        """
        Temporary for Diagnostics - Shows pyplot version of the data
        """
        fig = plt.figure()
        plt.plot(self.time, self.response, 'k-x')
        plt.xlabel(f"Time in {self.time_units}")
        plt.ylabel(f"Response in {self.response_units}")
        plt.show()

    def plot_pyplot_fft(self):
        """
        Temporary for Diagnostics - Checks to see if fft exists, then plots
        """
        try:
            resp = np.abs(self.fft_resp)
            fig = plt.figure()
            plt.semilogy(self.fft_freq, resp, 'k-x')
            plt.xlabel(f"Frequency in 1/{self.time_units}")
            plt.ylabel(f"Magnitude of Response in |{self.response_units}|")
            plt.show()
        except:
            print("FFT is not generated, please generate FFT data")

    def plot_pyplot_psd(self):
        """
        Temporary for Diagnostics - Checks to see if psd exists, then plots
        """
        try:
            resp = self.psd_resp
            fig = plt.figure()
            plt.plot(self.psd_freq, resp, 'k-x')
            plt.xlabel(f"Frequency in 1/{self.time_units}")
            plt.ylabel(f"Power Spectral Density in {self.response_units}^2")
            plt.show()
        except:
            print("PSD is not generated, please generate PSD data")

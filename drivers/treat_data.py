#%%
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
#%%
#%%
class treat_data:
    def __init__(self):
        self.c = 299792458  # speed of light in m/s
        return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return
    
    def wvl2freq(self, x, wvl0):
        """
        Convert wavelength to frequency
        
        input:
        x: np.array, wavelength data in NANOMETERS
        wvl0: float, reference wavelength NANOMETERS
        
        output:
        freq: np.array, frequency data in GHz
        """

        freq = self.c / ((x + wvl0)*1e-9) 
        freq = freq / 1e9 # convert to GHz
        return freq
         
    
    def chi_2(self, y_data, y_model, error):
        """
        Calculate the chi squared value
        
        input:
        data: np.array, data from the file
        model: np.array, model data
        error: np.array, error in the data
        
        output:
        chi_2: float, chi squared value
        """
        chi_2 = np.sum(((y_data - y_model) / error)**2)
        return chi_2
    
    def fwhm(self, x, y):
        """
        Calculate the full width at half maximum (FWHM) of a peak
        
        input:
        x: np.array, x data
        y: np.array, y data
        
        output:
        fwhm: float, full width at half maximum
        """
        
        half_max = (np.max(y) + np.min(y)) / 2.0
        idx = np.where(y > half_max)[0]
        if len(idx) == 0:
            return 0.0
        
        fwhm = x[idx[-1]] - x[idx[0]]
        return fwhm
    
    def fano_line(self, x, a, x0, gma, q, offset):
        """
        Fano line shape function
        
        input:
        x: np.array, x data
        a: float, amplitude of the line
        x0: float, center of the line
        gma: float, width of the line
        q: float, Fano factor

        output:
        y: np.array, y data
        """
        eps = 2 * (x - x0) / gma
        y = a * (q + eps)**2  / (1 + eps**2) + offset
        return y
    
    def smthng_fct(self, y, n=10):
        """
        Smooth the data using a moving average
        
        input: 
        y: np.array, y data
        n: int, window size for the moving average

        output:
        y_smooth: np.array, smoothed y data
        y_error: np.array, error in the smoothed data
        """

        y_smooth = np.zeros_like(y)
        y_error = np.zeros_like(y)

        n = int(n / 2)

        for i in range(len(y)):
            if i < n:
                y_smooth[i] = np.mean(y[:i+n])
                y_error[i] = np.std(y[:i+n])
            elif i >= len(y) - n:
                y_smooth[i] = np.mean(y[i-n:])
                y_error[i] = np.std(y[i-n:])
            else:
                y_smooth[i] = np.mean(y[i-n:i+n])
                y_error[i] = np.std(y[i-n:i+n])
        
        return y_smooth, y_error
        
    def fano_fit(self, x, y, yerr, p0=None, bounds=None):
        """
        Fit a Fano line shape to the data
        
        input:
        x: np.array, x data
        y: np.array, y data
        yerr: np.array, error in the data
        p0: list, initial guess for the parameters
        bounds: list, bounds for the parameters

        output:
        popt: list, optimal values for the parameters
        pcov: np.array, covariance matrix of the parameters
        """
        

        if p0 is None:
            
            amp_init = np.max(y) - np.min(y)
            x0_init = x[np.argmax(y)]
            gma_init = np.abs(self.fwhm(x, y) / 2.0)

            q_init = 0.1
            offset_init = np.min(y)

            p0 = [-amp_init, x0_init, gma_init, q_init, offset_init]
        
        if bounds is None:
            bounds = (
                [-np.inf, -np.inf, 0.0, -np.inf],
                [np.inf, np.inf, np.inf, np.inf]
                )
        
        print("p0: ", p0)
        popt, pcov = curve_fit(
            self.fano_line, x, y, p0=p0, sigma=yerr,
            #bounds=bounds
            )
        yguess = self.fano_line(x, *p0)
        y_fit = self.fano_line(x, *popt)
        
        plt.plot(x, y, label="data")
        # plt.plot(x, yguess, label="guess")
        plt.plot(x, y_fit, label="fit")
        plt.legend()
        plt.show()

        
        return popt, pcov
    
#%%


td = treat_data()


data = np.load("../output/input1/trace_ch1.npy")
n_points = data.shape[0]
# time_domain is the total time of the data in seconds
time_domain = 10 * 0.01 
# time_interval is the time interval between each point
time_interval = time_domain / n_points
print("time_interval: ", time_interval)
# setting time axis

time = np.arange(0, n_points) * time_interval

start_index = 100
end_index = 100000

subdatay = data[start_index:end_index]
subdatax = time[start_index:end_index]

smth_datay, y_err = td.smthng_fct(subdatay, n=10)


print("hihi")
print("number of points: ", subdatax.shape)
plt.plot(subdatax, subdatay, label="raw data")
plt.show()
plt.plot(subdatax, smth_datay, label="smoothed data")
plt.show()

#%%


# M is the [time -> wavelength] conversion factor
M = 5.18

wavelength_axis = subdatax * M
wvl0 = 1569.810 # reference wavelength in nm
plt.plot(wavelength_axis+wvl0, subdatay, label="raw data")
plt.show()


xfreq_axis = td.wvl2freq(wavelength_axis, wvl0)
xfreq_axis = np.array(xfreq_axis).astype(np.float64)
subdatay = np.array(subdatay).astype(np.float64)



popt, pcov = td.fano_fit(xfreq_axis, subdatay, None)
#popt_smth, _ = td.fano_fit(xfreq_axis, smth_datay, y_err)

print("popt: ", popt)
print("linewidth is: ", popt[2], "GHz")
print("error", np.sqrt(pcov[2][2]))



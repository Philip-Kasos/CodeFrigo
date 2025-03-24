import numpy as np

class treat_data:
    def __init__(self):
        return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return
    
    
    
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


    
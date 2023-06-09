 
from tqdm import tqdm

import scipy
import matplotlib.pyplot as plt
import numpy as np
import  pywt

from dataclasses import dataclass
##this fucntion assumes the waveeform is clean and have what we are after 
def compute_peak2peak_area(waveform):
    data_for_stats = waveform
    peak_to_peak = np.ptp(data_for_stats)
    
    dx = 0.1  # Spacing of integration points along axis of x
    area = scipy.integrate.simpson(abs(data_for_stats), dx=dx)
    return peak_to_peak, area

def _calculate_waveform_stats(waveform, start, end,triggerindex,times,baselinesd,baselineavg,artifactsrtaindex):
        
        data_for_stats = waveform[start:end]
        peak_to_peak = np.ptp(data_for_stats)
        dx = 0.1  # Spacing of integration points along axis of x
        area = scipy.integrate.simpson(abs(data_for_stats), dx=dx)
        #onsettime= calculateonset(waveform,triggerindex,start,end)
        #baselinesd= np.std([abs(num) for num in waveform[start:triggerindex]])
        #baselineavg=np.average([abs(num) for num in waveform[start:triggerindex]])
        
        onsetindex = findonset(waveform[triggerindex:end],baselinesd,baselineavg,artifactsrtaindex)
        #onsetindex=wavelet_onset_detection(np.array(waveform[triggerindex+20:end]),'sym4',4,3,artifactsrtaindex)
        try:
            if onsetindex==None:
                onsettime=None
            else:
                onsettime=times[onsetindex+triggerindex]
               
        except:
            pass

        
        return peak_to_peak, area
 

def plot(signal):
    wavelet = 'db4'  # Choose a wavelet
    level = 5# Choose a decomposition level
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    print(coeffs)
    reconstructed_signal = pywt.waverec(coeffs[:level], wavelet)
    # Plot the different levels of the decomposition
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))
    axs[0].plot(signal)
    axs[0].set_title("Original Signal")
    axs[1].plot(reconstructed_signal)
    axs[1].set_title(f"{level}-Level Reconstructed Signal")
    plt.tight_layout()
   

def findonset(evokedspan,baselinesdnew,baselineavg,artifactsrtaindex,threshold=1.5,ranged=1):
    onset=0

    #default values for threshold is 1.5 
    #default values for range is 1
    #for double likley need threshold 3, range 5 
    
    
    for i, x in enumerate(evokedspan):
        if i<=artifactsrtaindex:
            continue
        terminate=False
        print(f"length{len(evokedspan)}")
        print(i)
        if abs(x)-baselineavg > threshold* baselinesdnew :
            
            
            for p in range(ranged):
                if len(evokedspan)-i<ranged:
                    break
                elif abs(evokedspan[i + p])-baselineavg < threshold * baselinesdnew:
                    terminate=True
                    break
            

                onset = i
            
            if terminate==True:
                continue
            else:


                return onset-1

        else:
            continue


def findonsetnew(evokedspan,baselinesdnew,baselineavg,artifactsrtaindex):
    onset=0
    
    for i, x in enumerate(evokedspan):
        if i<=artifactsrtaindex:
            continue
        terminate=False
        print(f"length{len(evokedspan)}")
        print(i)
        if abs(x)-baselineavg > 2* baselinesdnew :
            
            
            for p in range(5):
                if len(evokedspan)-i<5:
                    break
                elif abs(evokedspan[i + p])-baselineavg < 2 * baselinesdnew:
                    terminate=True
                    break
            

                onset = i
            
            if terminate==True:
                continue
            else:


                return onset

        else:
            continue


def wavelet_onset_detection(signal, wavelet, level, threshold,artifactsrtaindex):
    ###this is not working yet 
    # Decompose signal into wavelet coefficients
    
    percent_changes = np.diff(signal) 
    coeff = pywt.wavedec(percent_changes[artifactsrtaindex:len(signal)-1], wavelet, mode="smooth",level=3)
    # Calculate a threshold for each level of the wavelet decomposition
    thresholds = [threshold*np.nanmedian(np.abs(c)) for c in coeff]
    # Set coefficients below the threshold to zero
    coeff[1:] = (pywt.threshold(i, value=t, mode='soft') for i, t in zip(coeff[1:], thresholds[1:]))
    # Reconstruct the signal using the modified coefficients
    reconstructed_signal = pywt.waverec(coeff, wavelet, mode='smooth')
    threshold = threshold*np.nanmedian(np.abs(signal))/0.6745
    onset = np.argmax(np.abs(reconstructed_signal) > threshold)
    # Calculate the onset as the point where the reconstructed signal first exceeds a threshold
    
    fig, axs = plt.subplots(3, 1, figsize=(10, 6))
    axs[0].plot(signal[artifactsrtaindex:])
    
    axs[0].set_title("Original Signal")
    axs[1].plot(percent_changes[artifactsrtaindex:])
    axs[1].set_title("Percentage change")
    axs[2].plot(reconstructed_signal)
    
    axs[2].set_title(f"{level}-Level Reconstructed Signal")
    #can i find the peak and then go to the left to find the point where thr value is increasing again
    plt.tight_layout()
    plt.show()
    plt.close()
    
    
    
    
    return onset+artifactsrtaindex
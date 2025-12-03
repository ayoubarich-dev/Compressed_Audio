import numpy as np

def channelsDistance(left,right):
    # Calculate difference metrics
    abs_diff = np.abs(left - right)
    mae = np.mean(abs_diff)  # Mean Absolute Error
    max_diff = np.max(abs_diff)
    std_diff = np.std(abs_diff)
    correlation = np.corrcoef(left, right)[0, 1]

    # Calculate energy ratio (how much energy is in the difference)
    mono = (left + right) / 2
    diff_signal = left - right
    energy_ratio = np.sum(diff_signal**2) / np.sum(mono**2)

    metrics = {
            'mean_absolute_diff': mae,
            'max_difference': max_diff,
            'std_difference': std_diff,
            'correlation': correlation,
            'energy_ratio': energy_ratio,
            'recommend_mono': energy_ratio < 0.2  # Threshold can be adjusted
        }
    return metrics

def process_stereo_sound(stereo_array):
    """
    Processes a stereo sound array by calculating the distance between channels
    and optionally removing one channel if the distance is below a threshold.

    Parameters:
        stereo_array (numpy.ndarray): A 2D array of shape (n_samples, 2) representing stereo sound.
        threshold (float): The threshold for the distance to decide if one channel should be removed.

    Returns:
        numpy.ndarray: A 1D array if one channel is removed, otherwise the original stereo array.
    """
    left = stereo_array[0:: 2]
    right = stereo_array[1:: 2]
    # Calculate the distance between the two channels
    metrics=channelsDistance(left,right)

    # Check if the distance is below the threshold
    if metrics["recommend_mono"]:
        # Remove one channel (e.g., keep the left channel)
        return {'mode': 'm'},left
    new_arr=np.empty(len(stereo_array),dtype=stereo_array.dtype)
    new_arr[0::2]=left
    new_arr[1::2]=left-right
    # Return one channel and the diff
    return {'mode': 's'},new_arr

def Back_to_real_stereo(array,mode):
    if mode=='m':
        new_arr=np.empty(len(array)*2,dtype=array.dtype)
        new_arr[0::2]=array[:]
        new_arr[1::2]=array[:]
    elif mode=='s':
        new_arr=np.empty(len(array)*2,dtype=array.dtype)
        left = array[0:: 2]
        diffright = array[1:: 2]
        right=left-diffright
        new_arr[0::2]=left
        new_arr[1::2]=right
    return new_arr  

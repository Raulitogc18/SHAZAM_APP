import numpy as np
from scipy.ndimage import maximum_filter
from scipy.signal import stft

# ------------------------------------------------------------------ #
# Parameters
# ------------------------------------------------------------------ #
SAMPLE_RATE = 22050
FFT_WINDOW_SIZE = 2048
HOP_SIZE = 1024

PEAK_NEIGHBORHOOD_TIME = 7
PEAK_NEIGHBORHOOD_FREQ = 7
MIN_PERCENTILE = 60

FREQ_BANDS = [
    (1, 10), (10, 20), (20, 40), (40, 80), (80, 160),
    (160, 256), (256, 384), (384, 512),
]

FAN_OUT = 15
TARGET_ZONE_START = 1
TARGET_ZONE_END = 50

FREQ_BITS = 12
DELTA_BITS = 12


# ------------------------------------------------------------------ #
# Spectrogram
# ------------------------------------------------------------------ #
def compute_spectrogram(audio, sample_rate=SAMPLE_RATE):
    freqs, times, Zxx = stft(
        audio,
        fs=sample_rate,
        nperseg=FFT_WINDOW_SIZE,
        noverlap=FFT_WINDOW_SIZE - HOP_SIZE,
    )

    magnitude = np.abs(Zxx)
    magnitude = 10 * np.log10(magnitude + 1e-10)
    magnitude -= magnitude.max()

    return freqs, times, magnitude


# ------------------------------------------------------------------ #
# Peak detection
# ------------------------------------------------------------------ #
def find_peaks(spec,
               neighborhood_freq=PEAK_NEIGHBORHOOD_FREQ,
               neighborhood_time=PEAK_NEIGHBORHOOD_TIME,
               min_percentile=MIN_PERCENTILE,
               freq_bands=FREQ_BANDS):

    n_freq, n_time = spec.shape
    threshold = np.percentile(spec, min_percentile)

    band_peaks = set()

    # STEP 1: band selection
    for t in range(n_time):
        for lo, hi in freq_bands:
            if lo >= n_freq:
                continue

            hi = min(hi, n_freq)
            band = spec[lo:hi, t]

            if band.size == 0:
                continue

            f_local = np.argmax(band)
            f_global = lo + f_local

            if spec[f_global, t] > threshold:
                band_peaks.add((t, f_global))

    # STEP 2: local max filter
    local_max = maximum_filter(spec, size=(neighborhood_freq, neighborhood_time))

    peaks = [
        (int(t), int(f))
        for (t, f) in band_peaks
        if spec[f, t] == local_max[f, t]
    ]

    return peaks


# ------------------------------------------------------------------ #
# Hashing
# ------------------------------------------------------------------ #
def hash_peak_pair(f1, f2, dt):
    return (int(f1) << (FREQ_BITS + DELTA_BITS)) | (int(f2) << DELTA_BITS) | int(dt)


# ------------------------------------------------------------------ #
# Fingerprint generation
# ------------------------------------------------------------------ #
def generate_fingerprints(peaks,
                          fan_out=FAN_OUT,
                          zone_start=TARGET_ZONE_START,
                          zone_end=TARGET_ZONE_END):

    peaks = sorted(peaks, key=lambda p: (p[0], p[1]))
    fingerprints = []

    for i in range(len(peaks)):
        t1, f1 = peaks[i]
        paired = 0

        for j in range(i + 1, len(peaks)):
            t2, f2 = peaks[j]
            dt = t2 - t1

            if dt < zone_start:
                continue
            if dt > zone_end:
                break

            h = hash_peak_pair(f1, f2, dt)
            fingerprints.append((h, t1))

            paired += 1
            if paired >= fan_out:
                break

    return fingerprints


# ------------------------------------------------------------------ #
# Full pipeline
# ------------------------------------------------------------------ #
def fingerprint_audio(audio, sample_rate=SAMPLE_RATE):
    _, _, spec = compute_spectrogram(audio, sample_rate)
    peaks = find_peaks(spec)
    return generate_fingerprints(peaks)
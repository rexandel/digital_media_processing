import numpy as np

class AudioEnhancer:
    def __init__(self):
        pass

    def custom_fft(self, signal):
        signal = np.asarray(signal, dtype=complex)
        signal_length = signal.shape[0]

        if signal_length <= 1:
            return signal
        
        even_part = self.custom_fft(signal[::2])
        odd_part = self.custom_fft(signal[1::2])
        twiddle_factors = np.exp(-2j * np.pi * np.arange(signal_length) / signal_length)

        return np.concatenate([
            even_part + twiddle_factors[:signal_length//2] * odd_part,
            even_part - twiddle_factors[:signal_length//2] * odd_part
        ])

    def custom_ifft(self, spectrum):
        spectrum = np.asarray(spectrum, dtype=complex)
        return np.conjugate(self.custom_fft(np.conjugate(spectrum))) / len(spectrum)

    def compute_stft(self, audio_signal, window_size=1024, hop_length=256, window_type='Ханна', use_numpy_fft=False):
        if window_type == 'Ханна':
            window_function = np.hanning(window_size)
        elif window_type == 'Хэмминга':
            window_function = np.hamming(window_size)
        elif window_type == 'Блэкмана':
            window_function = np.blackman(window_size)
        elif window_type == 'Барлетта':
            window_function = np.bartlett(window_size)
        elif window_type == 'Кайзера':
            window_function = np.kaiser(window_size, beta=14)
        else:
            window_function = np.hanning(window_size)
        
        stft_frames = []

        for frame_start in range(0, len(audio_signal) - window_size, hop_length):
            frame = audio_signal[frame_start:frame_start + window_size] * window_function
            if use_numpy_fft:
                stft_frames.append(np.fft.fft(frame))
            else:
                stft_frames.append(self.custom_fft(frame))

        return np.array(stft_frames), window_function

    def compute_istft(self, spectrogram, window_function, window_size=1024, hop_length=256, use_numpy_fft=False):
        output_length = hop_length * (len(spectrogram) + 1) + window_size
        reconstructed_signal = np.zeros(output_length)
        window_accumulator = np.zeros(output_length)

        current_position = 0
        for spectral_frame in spectrogram:
            if use_numpy_fft:
                time_frame = np.real(np.fft.ifft(spectral_frame))
            else:
                time_frame = np.real(self.custom_ifft(spectral_frame))

            reconstructed_signal[current_position:current_position+window_size] += time_frame * window_function
            window_accumulator[current_position:current_position+window_size] += window_function ** 2
            current_position += hop_length

        non_zero_indices = window_accumulator > 1e-8
        reconstructed_signal[non_zero_indices] /= window_accumulator[non_zero_indices]

        return reconstructed_signal

    def enhance_audio(self, audio_data, sample_rate, noise_sample_frames=80, noise_reduction_strength=5.5, spectral_floor_level=0.1, window_size=1024, hop_length=256, window_type='hann', use_numpy_fft=False, random_frames_seed=None):
        if audio_data.dtype != np.float32:
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            elif audio_data.dtype == np.float64:
                audio_data = audio_data.astype(np.float32)
            else:
                audio_data = audio_data.astype(np.float32)
        
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)
        
        fft_window = window_size
        frame_hop = hop_length

        spectrogram, analysis_window = self.compute_stft(
            audio_data, 
            window_size=fft_window, 
            hop_length=frame_hop,
            window_type=window_type,
            use_numpy_fft=use_numpy_fft
        )
        magnitude_spectrum = np.abs(spectrogram)
        phase_spectrum = np.angle(spectrogram)
        
        n_frames, n_freq_bins = magnitude_spectrum.shape
        
        if noise_sample_frames >= n_frames:
            selected_frame_indices = np.arange(n_frames)
        else:
            rng = np.random.default_rng(random_frames_seed)
            selected_frame_indices = rng.choice(
                n_frames, 
                size=min(noise_sample_frames, n_frames),
                replace=False
            )
        
        if len(selected_frame_indices) > 0:
            rng = np.random.default_rng(random_frames_seed)
            selected_freq_indices = rng.integers(
                0, n_freq_bins, 
                size=len(selected_frame_indices)
            )
            
            random_amplitudes = []
            for frame_idx, freq_idx in zip(selected_frame_indices, selected_freq_indices):
                random_amplitudes.append(magnitude_spectrum[frame_idx, freq_idx])
            
            random_amplitudes = np.array(random_amplitudes)
            percentile_amplitude = np.percentile(random_amplitudes, 25)

            noise_estimate = np.full(n_freq_bins, percentile_amplitude)
        else:
            noise_estimate = np.full(n_freq_bins, np.min(magnitude_spectrum))

        small_value = 1e-8
        noise_subtracted = magnitude_spectrum - noise_reduction_strength * noise_estimate[np.newaxis, :]

        suppression_gain = np.maximum(noise_subtracted / (magnitude_spectrum + small_value), spectral_floor_level)

        cleaned_spectrogram = suppression_gain * magnitude_spectrum * np.exp(1j * phase_spectrum)

        enhanced_audio = self.compute_istft(
            cleaned_spectrogram, 
            analysis_window, 
            window_size=fft_window, 
            hop_length=frame_hop,
            use_numpy_fft=use_numpy_fft
        )

        enhanced_audio = enhanced_audio[:len(audio_data)]
        enhanced_audio = np.clip(enhanced_audio, -1, 1)
        
        return enhanced_audio.astype(np.float32)
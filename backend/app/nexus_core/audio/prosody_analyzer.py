"""
Prosody Analyzer

Analyzes speech prosody: pitch, tone, rhythm, volume, speaking rate.
Key indicators of emotional state.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class ProsodyFeatures:
    """Prosody feature set"""
    pitch_mean: float  # Average pitch (relative to baseline)
    pitch_variance: float  # Pitch variability
    pitch_range: float  # Pitch range
    energy: float  # Volume/energy level
    speaking_rate: float  # Words/syllables per second
    pause_frequency: float  # Number of pauses
    pause_duration: float  # Average pause length
    rhythm_regularity: float  # Rhythm consistency
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'pitch_mean': self.pitch_mean,
            'pitch_variance': self.pitch_variance,
            'pitch_range': self.pitch_range,
            'energy': self.energy,
            'speaking_rate': self.speaking_rate,
            'pause_frequency': self.pause_frequency,
            'pause_duration': self.pause_duration,
            'rhythm_regularity': self.rhythm_regularity
        }


class ProsodyAnalyzer:
    """
    Prosody analyzer
    
    Extracts prosodic features from speech that indicate emotional state:
    - Pitch: Fundamental frequency (F0)
    - Energy: Volume/intensity
    - Rate: Speaking speed
    - Rhythm: Temporal patterns
    - Pauses: Silence patterns
    """
    
    def __init__(self):
        self.baseline_pitch = 150.0  # Hz (typical adult)
        self.baseline_energy = 0.5
        self.baseline_rate = 1.0
        
        try:
            import librosa
            self.librosa = librosa
            self._available = True
        except ImportError:
            self._available = False
            print("⚠ librosa not available. Install: pip install librosa")
    
    def analyze(self, audio_path: str) -> Dict[str, float]:
        """Analyze prosody from audio file"""
        if not self._available:
            return self._default_features()
        
        try:
            # Load audio
            y, sr = self.librosa.load(audio_path, sr=None)
            return self.analyze_array(y, sr)
        except Exception as e:
            print(f"Prosody analysis error: {e}")
            return self._default_features()
    
    def analyze_array(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze prosody from audio array"""
        if not self._available:
            return self._default_features()
        
        try:
            # Extract pitch (F0)
            pitch_features = self._extract_pitch(audio_data, sample_rate)
            
            # Extract energy
            energy = self._extract_energy(audio_data)
            
            # Extract speaking rate
            rate = self._extract_rate(audio_data, sample_rate)
            
            # Extract pauses
            pause_freq, pause_dur = self._extract_pauses(audio_data, sample_rate)
            
            # Extract rhythm
            rhythm = self._extract_rhythm(audio_data, sample_rate)
            
            return {
                'pitch_mean': pitch_features['mean'],
                'pitch_variance': pitch_features['variance'],
                'pitch_range': pitch_features['range'],
                'energy': energy,
                'speaking_rate': rate,
                'pause_frequency': pause_freq,
                'pause_duration': pause_dur,
                'rhythm_regularity': rhythm
            }
            
        except Exception as e:
            print(f"Prosody array analysis error: {e}")
            return self._default_features()
    
    def _extract_pitch(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract pitch features"""
        try:
            # Use librosa's pitch tracking (pyin algorithm)
            pitches, magnitudes = self.librosa.piptrack(y=audio, sr=sr)
            
            # Get pitch values (where magnitude > threshold)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if not pitch_values:
                return {'mean': 1.0, 'variance': 0.1, 'range': 0.2}
            
            pitch_values = np.array(pitch_values)
            
            # Calculate features (relative to baseline)
            mean = (np.mean(pitch_values) / self.baseline_pitch)
            variance = np.std(pitch_values) / self.baseline_pitch
            pitch_range = (np.max(pitch_values) - np.min(pitch_values)) / self.baseline_pitch
            
            return {
                'mean': mean,
                'variance': variance,
                'range': pitch_range
            }
        except Exception as e:
            return {'mean': 1.0, 'variance': 0.1, 'range': 0.2}
    
    def _extract_energy(self, audio: np.ndarray) -> float:
        """Extract energy (RMS)"""
        try:
            rms = np.sqrt(np.mean(audio ** 2))
            # Normalize to 0-1 range
            energy = min(1.0, rms * 10)  # Simple normalization
            return energy
        except:
            return 0.5
    
    def _extract_rate(self, audio: np.ndarray, sr: int) -> float:
        """Extract speaking rate"""
        try:
            # Detect onsets (syllables/words)
            onset_env = self.librosa.onset.onset_strength(y=audio, sr=sr)
            onsets = self.librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            
            # Calculate rate
            duration = len(audio) / sr
            if duration > 0:
                rate = len(onsets) / duration
                # Normalize relative to baseline (assume 3 syllables/sec baseline)
                normalized_rate = rate / 3.0
                return normalized_rate
            return 1.0
        except:
            return 1.0
    
    def _extract_pauses(self, audio: np.ndarray, sr: int) -> tuple:
        """Extract pause features (frequency, duration)"""
        try:
            # Detect silent periods
            intervals = self.librosa.effects.split(audio, top_db=30)
            
            if len(intervals) <= 1:
                return 0.0, 0.0
            
            # Calculate pauses between intervals
            pauses = []
            for i in range(len(intervals) - 1):
                pause_start = intervals[i][1]
                pause_end = intervals[i + 1][0]
                pause_length = (pause_end - pause_start) / sr
                pauses.append(pause_length)
            
            if not pauses:
                return 0.0, 0.0
            
            duration = len(audio) / sr
            pause_freq = len(pauses) / duration
            pause_dur = np.mean(pauses)
            
            return pause_freq, pause_dur
        except:
            return 0.0, 0.0
    
    def _extract_rhythm(self, audio: np.ndarray, sr: int) -> float:
        """Extract rhythm regularity"""
        try:
            # Use onset intervals to measure rhythm
            onset_env = self.librosa.onset.onset_strength(y=audio, sr=sr)
            onsets = self.librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            
            if len(onsets) < 3:
                return 0.5
            
            # Calculate inter-onset intervals
            intervals = np.diff(onsets)
            
            # Regularity = inverse of coefficient of variation
            if len(intervals) > 0 and np.mean(intervals) > 0:
                cv = np.std(intervals) / np.mean(intervals)
                regularity = 1.0 / (1.0 + cv)  # 0-1 range
                return regularity
            return 0.5
        except:
            return 0.5
    
    def _default_features(self) -> Dict[str, float]:
        """Return default features when analysis fails"""
        return {
            'pitch_mean': 1.0,
            'pitch_variance': 0.1,
            'pitch_range': 0.2,
            'energy': 0.5,
            'speaking_rate': 1.0,
            'pause_frequency': 0.0,
            'pause_duration': 0.0,
            'rhythm_regularity': 0.5
        }

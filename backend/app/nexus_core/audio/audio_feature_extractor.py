"""
Audio Feature Extractor

Extracts low-level audio features: MFCC, spectral features, zero-crossing rate.
Used for emotion classification and voice analysis.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class AudioFeatures:
    """Audio feature set"""
    mfcc_mean: np.ndarray  # MFCC mean values
    mfcc_std: np.ndarray  # MFCC standard deviations
    spectral_centroid: float  # Brightness indicator
    spectral_rolloff: float  # High-frequency content
    spectral_bandwidth: float  # Frequency spread
    zero_crossing_rate: float  # Noisiness indicator
    chroma_mean: np.ndarray  # Pitch class distribution
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mfcc_mean': self.mfcc_mean.tolist() if isinstance(self.mfcc_mean, np.ndarray) else self.mfcc_mean,
            'mfcc_std': self.mfcc_std.tolist() if isinstance(self.mfcc_std, np.ndarray) else self.mfcc_std,
            'spectral_centroid': self.spectral_centroid,
            'spectral_rolloff': self.spectral_rolloff,
            'spectral_bandwidth': self.spectral_bandwidth,
            'zero_crossing_rate': self.zero_crossing_rate,
            'chroma_mean': self.chroma_mean.tolist() if isinstance(self.chroma_mean, np.ndarray) else self.chroma_mean
        }


class AudioFeatureExtractor:
    """
    Audio feature extractor
    
    Extracts low-level acoustic features:
    - MFCC: Mel-frequency cepstral coefficients (timbre)
    - Spectral: Frequency domain characteristics
    - ZCR: Zero-crossing rate (noisiness)
    - Chroma: Pitch class distribution
    """
    
    def __init__(self, n_mfcc: int = 13, n_chroma: int = 12):
        self.n_mfcc = n_mfcc
        self.n_chroma = n_chroma
        
        try:
            import librosa
            self.librosa = librosa
            self._available = True
        except ImportError:
            self._available = False
            print("⚠ librosa not available. Install: pip install librosa")
    
    def extract(self, audio_path: str) -> Dict[str, Any]:
        """Extract features from audio file"""
        if not self._available:
            return self._default_features()
        
        try:
            # Load audio
            y, sr = self.librosa.load(audio_path, sr=None)
            return self.extract_from_array(y, sr)
        except Exception as e:
            print(f"Audio feature extraction error: {e}")
            return self._default_features()
    
    def extract_from_array(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract features from audio array"""
        if not self._available:
            return self._default_features()
        
        try:
            # Extract MFCC
            mfcc = self._extract_mfcc(audio_data, sample_rate)
            
            # Extract spectral features
            spectral = self._extract_spectral_features(audio_data, sample_rate)
            
            # Extract zero-crossing rate
            zcr = self._extract_zcr(audio_data)
            
            # Extract chroma features
            chroma = self._extract_chroma(audio_data, sample_rate)
            
            return {
                'mfcc_mean': mfcc['mean'],
                'mfcc_std': mfcc['std'],
                'spectral_centroid': spectral['centroid'],
                'spectral_rolloff': spectral['rolloff'],
                'spectral_bandwidth': spectral['bandwidth'],
                'zero_crossing_rate': zcr,
                'chroma_mean': chroma
            }
            
        except Exception as e:
            print(f"Audio array feature extraction error: {e}")
            return self._default_features()
    
    def _extract_mfcc(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Extract MFCC features"""
        try:
            # Compute MFCC
            mfcc = self.librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=self.n_mfcc)
            
            # Calculate statistics
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            return {
                'mean': mfcc_mean,
                'std': mfcc_std
            }
        except Exception as e:
            return {
                'mean': np.zeros(self.n_mfcc),
                'std': np.zeros(self.n_mfcc)
            }
    
    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features"""
        try:
            # Spectral centroid (brightness)
            centroid = self.librosa.feature.spectral_centroid(y=audio, sr=sr)
            centroid_mean = np.mean(centroid)
            
            # Spectral rolloff (high-frequency content)
            rolloff = self.librosa.feature.spectral_rolloff(y=audio, sr=sr)
            rolloff_mean = np.mean(rolloff)
            
            # Spectral bandwidth (frequency spread)
            bandwidth = self.librosa.feature.spectral_bandwidth(y=audio, sr=sr)
            bandwidth_mean = np.mean(bandwidth)
            
            # Normalize to 0-1 range
            centroid_norm = min(1.0, centroid_mean / 4000.0)  # ~4000Hz typical
            rolloff_norm = min(1.0, rolloff_mean / 8000.0)  # ~8000Hz typical
            bandwidth_norm = min(1.0, bandwidth_mean / 4000.0)
            
            return {
                'centroid': centroid_norm,
                'rolloff': rolloff_norm,
                'bandwidth': bandwidth_norm
            }
        except Exception as e:
            return {
                'centroid': 0.5,
                'rolloff': 0.5,
                'bandwidth': 0.5
            }
    
    def _extract_zcr(self, audio: np.ndarray) -> float:
        """Extract zero-crossing rate"""
        try:
            zcr = self.librosa.feature.zero_crossing_rate(audio)
            zcr_mean = np.mean(zcr)
            
            # Normalize to 0-1 range
            zcr_norm = min(1.0, zcr_mean * 10)  # Simple normalization
            return zcr_norm
        except:
            return 0.5
    
    def _extract_chroma(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extract chroma features (pitch class distribution)"""
        try:
            # Compute chroma features
            chroma = self.librosa.feature.chroma_stft(y=audio, sr=sr, n_chroma=self.n_chroma)
            
            # Calculate mean across time
            chroma_mean = np.mean(chroma, axis=1)
            
            return chroma_mean
        except Exception as e:
            return np.zeros(self.n_chroma)
    
    def _default_features(self) -> Dict[str, Any]:
        """Return default features when extraction fails"""
        return {
            'mfcc_mean': np.zeros(self.n_mfcc),
            'mfcc_std': np.zeros(self.n_mfcc),
            'spectral_centroid': 0.5,
            'spectral_rolloff': 0.5,
            'spectral_bandwidth': 0.5,
            'zero_crossing_rate': 0.5,
            'chroma_mean': np.zeros(self.n_chroma)
        }
    
    def extract_comprehensive(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive feature set for detailed analysis
        
        Returns all features plus additional metrics
        """
        if not self._available:
            return self._default_features()
        
        try:
            y, sr = self.librosa.load(audio_path, sr=None)
            
            # Get base features
            features = self.extract_from_array(y, sr)
            
            # Add additional features
            # Tempo
            tempo, _ = self.librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            
            # RMS Energy
            rms = self.librosa.feature.rms(y=y)
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # Spectral contrast
            contrast = self.librosa.feature.spectral_contrast(y=y, sr=sr)
            features['spectral_contrast_mean'] = np.mean(contrast, axis=1).tolist()
            
            # Tonnetz (harmonic features)
            tonnetz = self.librosa.feature.tonnetz(y=y, sr=sr)
            features['tonnetz_mean'] = np.mean(tonnetz, axis=1).tolist()
            
            return features
            
        except Exception as e:
            print(f"Comprehensive feature extraction error: {e}")
            return self._default_features()

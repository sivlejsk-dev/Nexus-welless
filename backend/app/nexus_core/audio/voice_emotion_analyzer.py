"""
Voice Emotion Analyzer

Main interface for analyzing emotions from speech audio.
Integrates prosody analysis with audio features to detect emotional state.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np


@dataclass
class VoiceEmotionData:
    """Voice-derived emotion data"""
    primary_emotion: str
    confidence: float
    intensity: float  # 0-1
    arousal: float  # 0-1 (calm to excited)
    valence: float  # -1 to 1 (negative to positive)
    prosody_features: Dict[str, float]
    audio_features: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_emotion': self.primary_emotion,
            'confidence': self.confidence,
            'intensity': self.intensity,
            'arousal': self.arousal,
            'valence': self.valence,
            'prosody': self.prosody_features,
            'audio': self.audio_features,
            'timestamp': self.timestamp.isoformat()
        }


class VoiceEmotionAnalyzer:
    """
    Voice emotion analyzer
    
    Analyzes speech audio to detect emotional state from:
    - Prosody (pitch, tone, rhythm, volume)
    - Audio features (MFCC, spectral characteristics)
    - Speaking rate and pauses
    
    Integrates with text-based emotion detection for comprehensive analysis.
    """
    
    def __init__(self):
        self.prosody_analyzer = None
        self.feature_extractor = None
        self._initialized = False
        
        # Emotion mappings (prosody-based)
        self.emotion_thresholds = {
            'happy': {'pitch': (1.2, 2.0), 'energy': (0.6, 1.0), 'rate': (1.1, 1.5)},
            'sad': {'pitch': (0.6, 0.9), 'energy': (0.2, 0.5), 'rate': (0.6, 0.9)},
            'angry': {'pitch': (1.3, 2.0), 'energy': (0.7, 1.0), 'rate': (1.2, 1.8)},
            'anxious': {'pitch': (1.1, 1.5), 'energy': (0.5, 0.8), 'rate': (1.3, 2.0)},
            'calm': {'pitch': (0.9, 1.1), 'energy': (0.3, 0.6), 'rate': (0.8, 1.1)},
            'neutral': {'pitch': (0.9, 1.1), 'energy': (0.4, 0.7), 'rate': (0.9, 1.2)}
        }
    
    def initialize(self):
        """Initialize analyzers (lazy loading)"""
        if self._initialized:
            return
        
        try:
            from .prosody_analyzer import ProsodyAnalyzer
            from .audio_feature_extractor import AudioFeatureExtractor
            
            self.prosody_analyzer = ProsodyAnalyzer()
            self.feature_extractor = AudioFeatureExtractor()
            self._initialized = True
            print("✓ Voice emotion analyzer initialized")
        except ImportError as e:
            print(f"⚠ Voice analysis dependencies not available: {e}")
            print("  Install: pip install librosa soundfile")
            self._initialized = False
    
    def analyze_audio_file(self, audio_path: str) -> Optional[VoiceEmotionData]:
        """
        Analyze emotion from audio file
        
        Args:
            audio_path: Path to audio file (.wav, .mp3, etc.)
            
        Returns:
            VoiceEmotionData or None if analysis fails
        """
        if not self._initialized:
            self.initialize()
        
        if not self._initialized:
            return None  # Dependencies not available
        
        try:
            # Extract audio features
            audio_features = self.feature_extractor.extract(audio_path)
            
            # Analyze prosody
            prosody_features = self.prosody_analyzer.analyze(audio_path)
            
            # Classify emotion
            emotion, confidence = self._classify_emotion(prosody_features, audio_features)
            
            # Calculate arousal and valence
            arousal = self._calculate_arousal(prosody_features)
            valence = self._calculate_valence(prosody_features, audio_features)
            intensity = prosody_features.get('energy', 0.5)
            
            return VoiceEmotionData(
                primary_emotion=emotion,
                confidence=confidence,
                intensity=intensity,
                arousal=arousal,
                valence=valence,
                prosody_features=prosody_features,
                audio_features=audio_features,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Voice emotion analysis error: {e}")
            return None
    
    def analyze_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[VoiceEmotionData]:
        """
        Analyze emotion from raw audio data
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            VoiceEmotionData or None if analysis fails
        """
        if not self._initialized:
            self.initialize()
        
        if not self._initialized:
            return None
        
        try:
            # Extract features from audio data
            audio_features = self.feature_extractor.extract_from_array(audio_data, sample_rate)
            prosody_features = self.prosody_analyzer.analyze_array(audio_data, sample_rate)
            
            # Classify emotion
            emotion, confidence = self._classify_emotion(prosody_features, audio_features)
            
            arousal = self._calculate_arousal(prosody_features)
            valence = self._calculate_valence(prosody_features, audio_features)
            intensity = prosody_features.get('energy', 0.5)
            
            return VoiceEmotionData(
                primary_emotion=emotion,
                confidence=confidence,
                intensity=intensity,
                arousal=arousal,
                valence=valence,
                prosody_features=prosody_features,
                audio_features=audio_features,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Voice emotion analysis error: {e}")
            return None
    
    def _classify_emotion(self, prosody: Dict[str, float], 
                         audio_features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Classify emotion from features
        
        Returns: (emotion, confidence)
        """
        pitch_ratio = prosody.get('pitch_mean', 1.0)
        energy = prosody.get('energy', 0.5)
        rate = prosody.get('speaking_rate', 1.0)
        
        scores = {}
        
        for emotion, thresholds in self.emotion_thresholds.items():
            score = 0.0
            
            # Check pitch
            pitch_min, pitch_max = thresholds['pitch']
            if pitch_min <= pitch_ratio <= pitch_max:
                score += 0.4
            
            # Check energy
            energy_min, energy_max = thresholds['energy']
            if energy_min <= energy <= energy_max:
                score += 0.3
            
            # Check speaking rate
            rate_min, rate_max = thresholds['rate']
            if rate_min <= rate <= rate_max:
                score += 0.3
            
            scores[emotion] = score
        
        # Get top emotion
        best_emotion = max(scores, key=scores.get)
        confidence = scores[best_emotion]
        
        return best_emotion, confidence
    
    def _calculate_arousal(self, prosody: Dict[str, float]) -> float:
        """Calculate arousal (calm to excited) from prosody"""
        energy = prosody.get('energy', 0.5)
        rate = prosody.get('speaking_rate', 1.0)
        pitch_var = prosody.get('pitch_variance', 0.5)
        
        # High energy, fast rate, high pitch variance = high arousal
        arousal = (energy + min(rate / 2, 0.5) + (pitch_var * 0.5)) / 2
        return min(1.0, max(0.0, arousal))
    
    def _calculate_valence(self, prosody: Dict[str, float],
                          audio_features: Dict[str, Any]) -> float:
        """Calculate valence (negative to positive) from features"""
        pitch = prosody.get('pitch_mean', 1.0)
        energy = prosody.get('energy', 0.5)
        
        # Higher pitch and energy typically correlate with positive valence
        valence = (pitch - 0.5) + (energy - 0.5)
        return min(1.0, max(-1.0, valence))
    
    def merge_with_text_emotion(self, voice_data: VoiceEmotionData,
                                text_emotion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge voice-based and text-based emotion analysis
        
        Args:
            voice_data: Voice emotion analysis
            text_emotion: Text-based emotion dict
            
        Returns:
            Merged emotion analysis
        """
        # Weight voice and text equally (can be tuned)
        voice_weight = 0.5
        text_weight = 0.5
        
        # If emotions match, increase confidence
        if voice_data.primary_emotion == text_emotion.get('primary_emotion'):
            confidence = min(1.0, voice_data.confidence + text_emotion.get('confidence', 0.5))
            return {
                'primary_emotion': voice_data.primary_emotion,
                'confidence': confidence,
                'intensity': (voice_data.intensity * voice_weight + 
                            text_emotion.get('intensity', 0.5) * text_weight),
                'arousal': voice_data.arousal,
                'valence': voice_data.valence,
                'sources': ['voice', 'text'],
                'agreement': True
            }
        else:
            # Emotions differ - use higher confidence
            if voice_data.confidence > text_emotion.get('confidence', 0.5):
                primary = voice_data.primary_emotion
                confidence = voice_data.confidence * 0.8  # Reduce due to disagreement
            else:
                primary = text_emotion.get('primary_emotion')
                confidence = text_emotion.get('confidence', 0.5) * 0.8
            
            return {
                'primary_emotion': primary,
                'confidence': confidence,
                'intensity': (voice_data.intensity * voice_weight + 
                            text_emotion.get('intensity', 0.5) * text_weight),
                'arousal': voice_data.arousal,
                'valence': voice_data.valence,
                'sources': ['voice', 'text'],
                'agreement': False,
                'voice_emotion': voice_data.primary_emotion,
                'text_emotion': text_emotion.get('primary_emotion')
            }

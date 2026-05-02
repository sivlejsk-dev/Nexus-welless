"""
Voice Emotion Analysis (Phase 8, Option B)

Analyzes audio features (prosody, tone, pitch, speed) to detect emotions from voice.
Integrates with existing emotional intelligence system.

Architecture:
    VoiceEmotionAnalyzer (main interface)
        ├── ProsodyAnalyzer (pitch, tone, rhythm)
        ├── AudioFeatureExtractor (MFCC, spectral features)
        ├── EmotionClassifier (voice → emotion mapping)
        └── IntegrationLayer (merge with text-based emotion)
"""

from .voice_emotion_analyzer import VoiceEmotionAnalyzer, VoiceEmotionData
from .prosody_analyzer import ProsodyAnalyzer, ProsodyFeatures
from .audio_feature_extractor import AudioFeatureExtractor, AudioFeatures

__all__ = [
    'VoiceEmotionAnalyzer',
    'VoiceEmotionData',
    'ProsodyAnalyzer',
    'ProsodyFeatures',
    'AudioFeatureExtractor',
    'AudioFeatures',
]

__version__ = '1.0.0'
__author__ = 'Nexus AI'

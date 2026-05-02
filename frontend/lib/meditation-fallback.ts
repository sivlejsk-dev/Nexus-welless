import type { MeditationGuide } from "@/lib/api";

export const fallbackMeditationGuides: MeditationGuide[] = [
  {
    id: "breathwork-box-beginner",
    title: "Box Breathing for Beginners",
    description: "Simple equal-count breathing to calm the nervous system: 4-4-4-4.",
    duration_minutes: 3,
    category: "breathwork",
    level: "beginner",
    tags: ["anxiety", "quick", "stress-relief", "focus"],
    audio_url: null,
    background_music: "/audio/music/ambient-calm-180bpm.wav",
    thumbnail_url: "/images/meditation/breathwork-box.jpg",
    voice_guidance: {
      speaker: "Sofia - Warm, Soothing Female",
      style: "gentle, encouraging",
      total_duration_seconds: 180,
      segments: [
        { time: 0, text: "Welcome to Box Breathing.", duration: 3 },
        { time: 3, text: "Find a comfortable seated position. Close your eyes when ready.", duration: 4 },
        { time: 7, text: "This technique balances your breath to calm your mind and body.", duration: 4 },
        { time: 11, text: "Inhale slowly through your nose for a count of four.", duration: 4 },
        { time: 15, text: "Hold your breath for a count of four.", duration: 4 },
        { time: 19, text: "Exhale slowly through your mouth for a count of four.", duration: 4 },
        { time: 23, text: "Hold empty for a count of four.", duration: 4 },
        { time: 27, text: "Ready? Let's begin.", duration: 2 },
      ],
    },
    script: [
      "Welcome to Box Breathing.",
      "Find a comfortable seated position. Close your eyes when ready.",
      "This technique balances your breath to calm your mind and body.",
      "We'll do four counts each: inhale, hold, exhale, hold.",
      "Ready? Let's begin.",
    ],
  },
  {
    id: "bodyscan-quick-beginner",
    title: "Quick Body Scan (5 min)",
    description: "Rapid progressive relaxation from head to toe for awareness and release.",
    duration_minutes: 5,
    category: "body-scan",
    level: "beginner",
    tags: ["quick", "relaxation", "awareness", "beginners"],
    audio_url: null,
    background_music: "/audio/music/soft-piano-ambient-80bpm.wav",
    thumbnail_url: "/images/meditation/bodyscan-quick.jpg",
    voice_guidance: {
      speaker: "Aria - Gentle, Nurturing Female",
      style: "warm, inviting, reassuring",
      total_duration_seconds: 300,
      segments: [
        { time: 0, text: "Welcome to a quick body scan.", duration: 2 },
        { time: 2, text: "Lie down on your back in a comfortable position.", duration: 3 },
        { time: 5, text: "Let your feet fall open naturally. Let your arms rest at your sides.", duration: 4 },
        { time: 9, text: "Take a deep breath in through your nose.", duration: 3 },
        { time: 12, text: "And exhale through your mouth.", duration: 3 },
      ],
    },
    script: [
      "Welcome to a quick body scan.",
      "Lie on your back in a comfortable position.",
      "Let your body be fully supported.",
      "Bring awareness to your head - notice sensations, release tension.",
      "Gently return to movement and open your eyes.",
    ],
  },
  {
    id: "visualization-morning-intention-beginner",
    title: "Morning Intention Visualization",
    description: "Set your day's direction with clarity and positive energy.",
    duration_minutes: 7,
    category: "visualization",
    level: "beginner",
    tags: ["morning", "intention", "focus", "energy"],
    audio_url: null,
    background_music: "/audio/music/uplifting-morning-100bpm.wav",
    thumbnail_url: "/images/meditation/morning-intention.jpg",
    voice_guidance: {
      speaker: "Luna - Bright, Energetic Female",
      style: "inspiring, clear, empowering",
      total_duration_seconds: 420,
      segments: [
        { time: 0, text: "Welcome to your morning intention practice.", duration: 3 },
        { time: 3, text: "Sit tall and let your breath become steady.", duration: 4 },
        { time: 7, text: "Imagine the day ahead unfolding with ease.", duration: 4 },
        { time: 11, text: "Choose one clear intention to carry with you.", duration: 4 },
      ],
    },
    script: [
      "Welcome to your morning intention practice.",
      "Sit tall and let your breath become steady.",
      "Imagine the day ahead unfolding with ease.",
      "Choose one clear intention to carry with you.",
    ],
  },
  {
    id: "mantra-om-beginner",
    title: "OM Mantra Meditation",
    description: "Simple mantra meditation using the universal sound OM.",
    duration_minutes: 5,
    category: "mantra",
    level: "beginner",
    tags: ["mantra", "sacred-sound", "beginner", "universal"],
    audio_url: null,
    background_music: "/audio/music/om-frequency-108hz.wav",
    thumbnail_url: "/images/meditation/om-mantra.jpg",
    voice_guidance: {
      speaker: "Vedic Scholar - Authentic Sanskrit",
      style: "traditional, reverent, clear",
      total_duration_seconds: 300,
      segments: [
        { time: 0, text: "Welcome to OM mantra meditation.", duration: 3 },
        { time: 3, text: "Let the breath settle and soften.", duration: 3 },
        { time: 6, text: "On each exhale, gently chant OM.", duration: 4 },
        { time: 10, text: "Feel the vibration through your chest and throat.", duration: 4 },
      ],
    },
    script: [
      "Welcome to OM mantra meditation.",
      "Let the breath settle and soften.",
      "On each exhale, gently chant OM.",
      "Feel the vibration through your chest and throat.",
    ],
  },
];

export function getFallbackMeditationGuides(params?: { category?: string; tag?: string; level?: string }) {
  return fallbackMeditationGuides.filter((guide) => {
    if (params?.category && guide.category !== params.category) {
      return false;
    }
    if (params?.level && guide.level !== params.level) {
      return false;
    }
    if (params?.tag && !guide.tags.some((tag) => tag.toLowerCase() === params.tag?.toLowerCase())) {
      return false;
    }
    return true;
  });
}

import type {
  MediaGuide,
  MediaGuideInfo,
  MediaGuideStep,
  MediaImage,
  MediaQueryResult,
} from "@/lib/api";

export interface MediaVideo {
  id: string;
  title: string;
  description: string;
  category: string;
  duration: string;
  embed_url: string;
  thumbnail: MediaImage;
  steps: string[];
}

const visualThemes: Record<string, { a: string; b: string; c: string; icon: string }> = {
  nutrition: { a: "#0f766e", b: "#84cc16", c: "#f8fafc", icon: "🥗" },
  meditation: { a: "#4338ca", b: "#38bdf8", c: "#f8fafc", icon: "🧘" },
  detox: { a: "#047857", b: "#22d3ee", c: "#f8fafc", icon: "💧" },
  herbs: { a: "#166534", b: "#facc15", c: "#f8fafc", icon: "🌿" },
  cooking: { a: "#7c2d12", b: "#fb923c", c: "#fff7ed", icon: "🍳" },
  fitness: { a: "#be123c", b: "#f97316", c: "#fff1f2", icon: "🏃" },
  sleep: { a: "#312e81", b: "#a78bfa", c: "#f5f3ff", icon: "🌙" },
  general: { a: "#0f172a", b: "#8b5cf6", c: "#f8fafc", icon: "✨" },
};

function imageDataUrl(topic = "general", label = "Wellness visual"): string {
  const theme = visualThemes[topic] ?? visualThemes.general;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="${theme.a}"/>
          <stop offset="1" stop-color="${theme.b}"/>
        </linearGradient>
        <radialGradient id="r" cx="72%" cy="18%" r="70%">
          <stop offset="0" stop-color="${theme.c}" stop-opacity=".38"/>
          <stop offset="1" stop-color="${theme.c}" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="1200" height="820" fill="url(#g)"/>
      <rect width="1200" height="820" fill="url(#r)"/>
      <circle cx="185" cy="655" r="170" fill="${theme.c}" opacity=".10"/>
      <circle cx="980" cy="150" r="230" fill="${theme.c}" opacity=".12"/>
      <text x="92" y="184" font-size="104" font-family="Arial, sans-serif">${theme.icon}</text>
      <text x="92" y="292" fill="${theme.c}" font-size="56" font-family="Arial, sans-serif" font-weight="700">${label}</text>
      <text x="96" y="354" fill="${theme.c}" opacity=".76" font-size="28" font-family="Arial, sans-serif">Nexus Wellness visual guide</text>
    </svg>
  `;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function fallbackImage(topic: string, label: string): MediaImage {
  return {
    url: imageDataUrl(topic, label),
    source: "local",
    prompt: label,
    revised_prompt: null,
    dalle_available: false,
  };
}

function step(
  step_number: number,
  title: string,
  description: string,
  action: string,
  icon: string,
  topic: string,
): MediaGuideStep {
  return {
    step_number,
    title,
    description,
    action,
    icon,
    image: fallbackImage(topic, title),
  };
}

export const fallbackGuides: MediaGuide[] = [
  {
    id: "anti-inflammatory-protocol",
    title: "Anti-Inflammatory Protocol",
    subtitle: "A practical food-as-medicine reset",
    total_steps: 5,
    images_generated: false,
    steps: [
      step(1, "Remove Triggers", "Reduce refined sugar, alcohol, seed oils, and ultra-processed foods for one week.", "Choose one shelf or drawer and clear the obvious inflammatory foods today.", "🚫", "nutrition"),
      step(2, "Morning Tonic", "Start with warm lemon water, turmeric, and black pepper to support digestion.", "Prep lemon, turmeric, and pepper beside your kettle tonight.", "🌅", "herbs"),
      step(3, "Build the Plate", "Aim for colorful plants, clean protein, slow carbohydrates, and healthy fats.", "Use the 50/25/25 plate: vegetables, protein, smart carbs.", "🥗", "nutrition"),
      step(4, "Add Omega-3s", "Use wild fish, chia, flax, walnuts, or a quality EPA/DHA supplement.", "Add one omega-3 source to lunch or dinner.", "🐟", "nutrition"),
      step(5, "Wind Down", "Sleep quality strongly influences inflammatory markers and recovery.", "Dim lights one hour before bed and take a slow breathing break.", "🌙", "sleep"),
    ],
  },
  {
    id: "gut-healing-5r",
    title: "5R Gut Healing Protocol",
    subtitle: "Remove, Replace, Reinoculate, Repair, Rebalance",
    total_steps: 5,
    images_generated: false,
    steps: [
      step(1, "Remove", "Temporarily remove common irritants and track symptoms without overcomplicating the process.", "Keep a two-week food and symptom note.", "🚫", "nutrition"),
      step(2, "Replace", "Support digestive capacity with mindful chewing, bitters, enzymes, or clinician-guided support.", "Take five slow breaths before meals.", "⚗️", "detox"),
      step(3, "Reinoculate", "Bring in fermented foods and prebiotic fibers gradually.", "Add one tablespoon of fermented food daily.", "🦠", "detox"),
      step(4, "Repair", "Prioritize zinc, protein, collagen-rich foods, and soothing broths.", "Add a protein-rich breakfast this week.", "🔧", "nutrition"),
      step(5, "Rebalance", "Stress, sleep, movement, and connection shape gut function every day.", "Schedule a 10-minute walk after one meal.", "⚖️", "meditation"),
    ],
  },
  {
    id: "morning-wellness-ritual",
    title: "Morning Wellness Ritual",
    subtitle: "A steady start for energy, mood, and focus",
    total_steps: 5,
    images_generated: false,
    steps: [
      step(1, "Hydrate", "Replenish fluid before caffeine or screens.", "Place water by your bed before sleep.", "💧", "detox"),
      step(2, "Get Light", "Morning light helps anchor your circadian rhythm.", "Step outside for 5 to 10 minutes.", "☀️", "fitness"),
      step(3, "Move Gently", "Light motion wakes up joints, circulation, and attention.", "Do five minutes of mobility or walking.", "🏃", "fitness"),
      step(4, "Eat for Stability", "Protein, fiber, and healthy fats reduce mid-morning crashes.", "Build breakfast around protein plus plants.", "🥗", "nutrition"),
      step(5, "Set Intent", "A brief intentional pause helps you choose the tone of the day.", "Write one priority and one thing you are grateful for.", "📝", "meditation"),
    ],
  },
  {
    id: "plant-based-meat-mastery",
    title: "Plant-Based Meat Mastery",
    subtitle: "Texture, browning, smoke, and umami",
    total_steps: 4,
    images_generated: false,
    steps: [
      step(1, "Dry the Protein", "Moisture blocks browning. Press tofu, pat mushrooms, and drain jackfruit well.", "Press tofu for 20 minutes before cooking.", "💨", "cooking"),
      step(2, "Layer Umami", "Miso, tamari, nutritional yeast, tomato paste, and mushroom powder create depth.", "Mix a quick marinade with tamari, miso, and smoked paprika.", "🧂", "cooking"),
      step(3, "Use High Heat", "A hot pan creates the browned surface that makes plant proteins satisfying.", "Preheat the pan before the protein goes in.", "🔥", "cooking"),
      step(4, "Finish with Contrast", "Acid, herbs, crunch, and sauce make the final bite feel complete.", "Finish with lemon, herbs, and toasted seeds.", "🌿", "nutrition"),
    ],
  },
];

export const fallbackVideos: MediaVideo[] = [
  {
    id: "breathwork-reset-video",
    title: "Guided Breathwork Reset",
    description: "A calm visual breathing session for settling the nervous system.",
    category: "meditation",
    duration: "4 min",
    embed_url: "https://www.youtube.com/embed/inpok4MKVLM",
    thumbnail: fallbackImage("meditation", "Guided Breathwork Reset"),
    steps: ["Sit comfortably", "Inhale gently", "Exhale slowly", "Repeat without strain"],
  },
  {
    id: "morning-mobility-video",
    title: "Morning Mobility Flow",
    description: "A simple movement flow to pair with the morning wellness ritual.",
    category: "fitness",
    duration: "8 min",
    embed_url: "https://www.youtube.com/embed/4pKly2JojMw",
    thumbnail: fallbackImage("fitness", "Morning Mobility Flow"),
    steps: ["Open shoulders", "Mobilize spine", "Wake hips", "Finish with breathing"],
  },
  {
    id: "anti-inflammatory-meal-video",
    title: "Anti-Inflammatory Meal Build",
    description: "A practical visual walkthrough for building a healing plate.",
    category: "nutrition",
    duration: "6 min",
    embed_url: "https://www.youtube.com/embed/xyQY8a-ng6g",
    thumbnail: fallbackImage("nutrition", "Anti-Inflammatory Meal Build"),
    steps: ["Choose colorful plants", "Add protein", "Add omega-3 fats", "Season with herbs"],
  },
];

export function fallbackGuideList(): MediaGuideInfo[] {
  return fallbackGuides.map((guide) => ({
    id: guide.id,
    title: guide.title,
    subtitle: guide.subtitle,
    step_count: guide.total_steps,
  }));
}

export function getFallbackGuide(id: string): MediaGuide | undefined {
  return fallbackGuides.find((guide) => guide.id === id);
}

export function getFallbackMedia(query: string, mediaType: "auto" | "image" | "guide" | "video" = "auto"): MediaQueryResult {
  const q = query.toLowerCase();
  const wantsVideo = mediaType === "video" || /\b(video|watch|movement|mobility|flow)\b/.test(q);
  if (wantsVideo) {
    const video = fallbackVideos.find((item) => q.includes(item.category) || q.includes(item.title.toLowerCase().split(" ")[0])) ?? fallbackVideos[0];
    return { type: "video", data: video };
  }

  const guide = fallbackGuides.find((item) =>
    q.includes(item.id.replace(/-/g, " ")) ||
    item.title.toLowerCase().split(/\s+/).some((word) => word.length > 4 && q.includes(word)),
  );
  const wantsGuide = mediaType === "guide" || /\b(guide|steps|protocol|routine|ritual|how to|plan)\b/.test(q);
  if (wantsGuide) {
    return guide ? { type: "guide", data: guide } : { type: "guide_list", data: fallbackGuideList() };
  }

  const topic = Object.keys(visualThemes).find((key) => q.includes(key)) ?? "general";
  return {
    type: "image",
    data: fallbackImage(topic, query || "Wellness visual"),
  };
}

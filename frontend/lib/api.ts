/**
 * Typed API client for the Nexus Wellness backend.
 * All requests include the JWT from localStorage when available.
 * On 401, the access token is silently refreshed once and the request retried.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API = `${BASE_URL}/api/v1`;

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nexus_access_token");
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nexus_refresh_token");
}

function setTokens(access: string, refresh: string): void {
  localStorage.setItem("nexus_access_token", access);
  localStorage.setItem("nexus_refresh_token", refresh);
}

function clearTokens(): void {
  localStorage.removeItem("nexus_access_token");
  localStorage.removeItem("nexus_refresh_token");
}

// Prevent concurrent refresh races — one in-flight refresh shared by all callers.
let _refreshPromise: Promise<string | null> | null = null;

async function _doRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;
  try {
    const res = await fetch(`${API}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) { clearTokens(); return null; }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  if (!_refreshPromise) {
    _refreshPromise = _doRefresh().finally(() => { _refreshPromise = null; });
  }
  return _refreshPromise;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  _retry = true,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 90_000);

  try {
    const res = await fetch(`${API}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    // On 401, attempt a silent token refresh then retry once.
    if (res.status === 401 && _retry) {
      clearTimeout(timeout);
      const newToken = await refreshAccessToken();
      if (newToken) {
        return request<T>(path, options, false);
      }
      // Refresh failed — redirect to login.
      if (typeof window !== "undefined") window.location.href = "/login";
      throw new Error("Session expired. Please log in again.");
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail ?? "Request failed");
    }
    return res.json() as Promise<T>;
  } finally {
    clearTimeout(timeout);
  }
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const auth = {
  register: (email: string, password: string, full_name?: string) =>
    request<{ access_token: string; refresh_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  guest: () =>
    request<{ access_token: string; refresh_token: string }>("/auth/guest", {
      method: "POST",
    }),
};

// ── Users ─────────────────────────────────────────────────────────────────────
export const users = {
  me: () => request<User>("/users/me"),
  getProfile: () => request<WellnessProfile>("/users/me/profile"),
  updateProfile: (data: Partial<WellnessProfile>) =>
    request<WellnessProfile>("/users/me/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// ── Meditation ────────────────────────────────────────────────────────────────
export const meditation = {
  guides: (params?: { category?: string; tag?: string; level?: string }) => {
    const q = new URLSearchParams(params as Record<string, string>).toString();
    return request<MeditationGuide[]>(`/meditation/guides${q ? `?${q}` : ""}`);
  },
  guide: (id: string) => request<MeditationGuide>(`/meditation/guides/${id}`),
  recommended: () => request<MeditationGuide[]>("/meditation/recommended"),
  nexusInsight: () => request<NexusResponse>("/meditation/nexus-insight"),
  logSession: (data: SessionLog) =>
    request<SessionLog>("/meditation/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ── Nutrition ─────────────────────────────────────────────────────────────────
export const nutrition = {
  search: (q: string, limit = 10) =>
    request<{ results: FoodResult[]; count: number }>(
      `/nutrition/search?q=${encodeURIComponent(q)}&limit=${limit}`
    ),
  healingFoods: (condition: string) =>
    request<{ condition: string; foods: HealingFood[] }>(
      `/nutrition/healing-foods?condition=${encodeURIComponent(condition)}`
    ),
  mealPlan: (focus = "anti-inflammatory", days = 7) =>
    request<MealPlan[]>(`/nutrition/meal-plan?focus=${focus}&days=${days}`),
  recommendation: (condition: string) =>
    request<NutritionRec>(`/nutrition/recommendation?condition=${encodeURIComponent(condition)}`),
};

// ── Astrology ─────────────────────────────────────────────────────────────────
export const astrology = {
  horoscope: (sign: string) =>
    request<Horoscope>(`/astrology/horoscope/${sign}`),
  myHoroscope: () => request<Horoscope>("/astrology/horoscope/me/today"),
  myChart: () => request<BirthChart>("/astrology/my-chart"),
  signs: () => request<SignProfile[]>("/astrology/signs"),
};

// ── Detox ─────────────────────────────────────────────────────────────────────
export const detox = {
  protocols: (intensity?: string) =>
    request<DetoxProtocol[]>(
      `/detox/protocols${intensity ? `?intensity=${intensity}` : ""}`
    ),
  protocol: (id: string) => request<DetoxProtocol>(`/detox/protocols/${id}`),
  dayGuidance: (protocolId: string, day: number) =>
    request<DayGuidance>(`/detox/protocols/${protocolId}/day/${day}`),
  recommended: () => request<DetoxProtocol>("/detox/recommended"),
  logDay: (data: DetoxLogEntry) =>
    request<DetoxLogEntry>("/detox/logs", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ── Nexus AI ──────────────────────────────────────────────────────────────────
export interface NexusSession {
  session_id: string;
  primary_domain: string | null;
  total_turns: number;
  active_turns: number;
  has_summary: boolean;
  summary_preview: string | null;
  created_at: string;
  last_active: string;
}

export interface NexusTurn {
  turn_index: number;
  role: "user" | "assistant";
  content: string;
  domain: string | null;
  intent: string | null;
  created_at: string;
}

export interface NexusSessionDetail extends NexusSession {
  summary: string | null;
  turns: NexusTurn[];
}

export const nexus = {
  recommend: (module: string, context: Record<string, unknown> = {}, user_message?: string) =>
    request<NexusResponse>("/nexus/recommend", {
      method: "POST",
      body: JSON.stringify({ module, context, user_message }),
    }),

  chat: (message: string, module?: string) =>
    request<NexusChatResponse>("/nexus/chat", {
      method: "POST",
      body: JSON.stringify({ message: module ? `[${module}] ${message}` : message }),
    }),

  /** List the current user's conversation sessions, most recent first. */
  listSessions: (limit = 20) =>
    request<{ sessions: NexusSession[]; count: number }>(`/nexus/sessions?limit=${limit}`),

  /** Fetch full turn history for a specific session. */
  getSession: (sessionId: string) =>
    request<NexusSessionDetail>(`/nexus/sessions/${sessionId}`),

  /** Delete a specific session. */
  deleteSession: (sessionId: string) =>
    request<{ deleted: boolean }>(`/nexus/sessions/${sessionId}`, { method: "DELETE" }),

  /** Clear the active in-memory conversation context. */
  clearSession: () =>
    request<{ cleared: boolean }>("/nexus/session", { method: "DELETE" }),
};

// ── Media / Console ───────────────────────────────────────────────────────────

export const mediaApi = {
  config: () => request<MediaConfig>("/media/config"),
  guides: () => request<MediaGuideInfo[]>("/media/guides"),
  guide: (id: string, dalle = false) =>
    request<MediaGuide>(`/media/guides/${id}?dalle=${dalle}`),
  generate: (prompt: string, topic = "general", size = "1024x1024") =>
    request<MediaImage>("/media/generate", {
      method: "POST",
      body: JSON.stringify({ prompt, topic, size }),
    }),
  query: (query: string, media_type = "auto") =>
    request<MediaQueryResult>("/media/query", {
      method: "POST",
      body: JSON.stringify({ query, media_type }),
    }),
  generateVideo: (prompt: string, size = "1280x720", seconds = "8", model?: string) =>
    request<MediaProviderJob>("/media/video/generate", {
      method: "POST",
      body: JSON.stringify({ prompt, size, seconds, model }),
    }),
  getVideo: (videoId: string) =>
    request<MediaProviderJob>(`/media/video/${videoId}`),
  generateMusic: (prompt: string, provider = "auto", title?: string, instrumental = true) =>
    request<MediaProviderJob>("/media/music/generate", {
      method: "POST",
      body: JSON.stringify({ prompt, provider, title, instrumental }),
    }),
};

// ── Meat Substitutes ──────────────────────────────────────────────────────────

export const meatSubs = {
  bases: () => request<MeatSubBase[]>("/meat-substitutes/bases"),
  base: (id: string) => request<MeatSubBase>(`/meat-substitutes/bases/${id}`),
  recipes: (craving?: string) =>
    request<MeatSubRecipe[]>(`/meat-substitutes/recipes${craving ? `?craving=${encodeURIComponent(craving)}` : ""}`),
  recipe: (id: string) => request<MeatSubRecipe>(`/meat-substitutes/recipes/${id}`),
  forMeat: (meatType: string) => request<MeatSubForMeat>(`/meat-substitutes/for/${encodeURIComponent(meatType)}`),
  techniques: () => request<MeatSubTechnique[]>("/meat-substitutes/techniques"),
  nutritionComparison: () => request<Record<string, unknown>>("/meat-substitutes/nutrition-comparison"),
};

// ── Voice ─────────────────────────────────────────────────────────────────────

/** Upload audio blob and get back transcript + Nexus response + optional MP3. */
export async function voiceChat(
  audioBlob: Blob,
  opts: { voice?: string; voiceSpeed?: number; ttsEnabled?: boolean; language?: string } = {}
): Promise<VoiceChatResponse> {
  const token = getToken();

  // Set filename based on blob type
  let filename = "audio.webm";
  if (audioBlob.type.includes("mp4")) filename = "audio.mp4";
  else if (audioBlob.type.includes("ogg")) filename = "audio.ogg";
  else if (audioBlob.type.includes("wav")) filename = "audio.wav";

  const form = new FormData();
  form.append("audio", audioBlob, filename);
  form.append("voice", opts.voice ?? "shimmer");
  form.append("speed", String(opts.voiceSpeed ?? 0.88));
  form.append("tts_enabled", (opts.ttsEnabled ?? true).toString());
  if (opts.language) form.append("language", opts.language);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);

  try {
    const res = await fetch(`${API}/voice/chat`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
      signal: controller.signal,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? "Voice chat failed");
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

/** Transcribe audio only (no chat). */
export async function transcribeAudio(
  audioBlob: Blob,
  language?: string
): Promise<{ transcript: string; language: string | null; configured: boolean }> {
  const token = getToken();
  const form = new FormData();
  form.append("audio", audioBlob, "audio.webm");
  if (language) form.append("language", language);

  const res = await fetch(`${API}/voice/transcribe`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Transcription failed");
  }
  return res.json();
}

/** Fetch voice capability config. */
export async function getVoiceConfig(): Promise<VoiceConfig> {
  return request<VoiceConfig>("/voice/config");
}

/** Namespaced voice helpers used by useVoice. */
export const voice = {
  /**
   * Synthesise text to speech.
   * Calls POST /voice/synthesise which returns raw MP3 bytes.
   * Converts to base64 so it can be played via an Audio element.
   * Returns null on any failure (TTS is non-critical).
   */
  async synthesise(text: string, voiceName = "shimmer", speed = 0.88): Promise<string | null> {
    const token = getToken();
    const form = new FormData();
    form.append("text", text.slice(0, 4096));
    form.append("voice", voiceName);
    form.append("speed", String(speed));

    try {
      const res = await fetch(`${API}/voice/synthesise`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      if (!res.ok) return null;
      const arrayBuf = await res.arrayBuffer();
      // Convert binary MP3 to base64 for Audio element playback
      const bytes = new Uint8Array(arrayBuf);
      let binary = "";
      for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
      return btoa(binary);
    } catch {
      return null;
    }
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
}

export interface WellnessProfile {
  date_of_birth?: string;
  birth_time?: string;
  birth_location?: string;
  birth_lat?: number;
  birth_lon?: number;
  timezone?: string;
  height_cm?: number;
  weight_kg?: number;
  dietary_preferences?: string[];
  health_goals?: string[];
  allergies?: string[];
  conditions?: string[];
  sun_sign?: string;
  moon_sign?: string;
  rising_sign?: string;
}

export interface MeditationGuide {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  category: string;
  level: string;
  tags: string[];
  audio_url: string | null;
  background_music?: string | null;
  voice_guidance?: {
    speaker?: string;
    style?: string;
    total_duration_seconds?: number;
    segments?: { time: number; text: string; duration?: number }[];
  } | null;
  thumbnail_url: string | null;
  script?: string[];
}

export interface SessionLog {
  guide_id: string;
  duration_seconds: number;
  completed: boolean;
  mood_before?: number;
  mood_after?: number;
  notes?: string;
}

export interface FoodResult {
  fdcId: number;
  description: string;
  brandOwner?: string;
  foodCategory?: string;
  foodNutrients?: Array<{ nutrientName: string; value: number; unitName: string }>;
}

export interface HealingFood {
  name: string;
  properties: string[];
  active_compound: string;
  best_for: string[];
  preparation: string;
}

export interface MealPlan {
  day: number;
  meals: Array<{ meal: string; foods: string[]; notes: string }>;
  total_calories: number;
  macros: { protein_g: number; carbs_g: number; fat_g: number; fiber_g: number };
  healing_focus: string;
}

export interface NutritionRec {
  condition: string;
  foods: HealingFood[];
  avoid: string[];
  rationale: string;
  nexus_insight?: string;
}

export interface Horoscope {
  sign: string;
  date: string;
  general: string;
  love: string;
  career: string;
  health: string;
  lucky_number: number;
  lucky_color: string;
  nexus_insight?: string;
}

export interface BirthChart {
  sun: PlanetPos;
  moon: PlanetPos;
  rising: PlanetPos;
  planets: PlanetPos[];
  houses: Array<{ house: number; degree: number; sign: string }>;
  aspects: Array<{ planet1: string; planet2: string; aspect: string; orb: number }>;
  nexus_interpretation?: string;
}

export interface PlanetPos {
  planet: string;
  sign: string;
  degree: number;
  house?: number;
  retrograde: boolean;
}

export interface SignProfile {
  sign: string;
  element: string;
  modality: string;
  body_area: string;
  healing_focus: string;
  meditation: string;
}

export interface DetoxProtocol {
  id: string;
  name: string;
  description: string;
  duration_days: number;
  intensity: string;
  phases: DetoxPhase[];
  contraindications: string[];
  supplements: string[];
}

export interface DetoxPhase {
  phase: number;
  days: string;
  name: string;
  focus: string;
  eat: string[];
  avoid: string[];
  practices: string[];
  expected_symptoms: string[];
}

export interface DayGuidance {
  protocol: string;
  day: number;
  phase: string;
  focus: string;
  eat: string[];
  avoid: string[];
  practices: string[];
  expected_symptoms: string[];
  supplements: string[];
}

export interface DetoxLogEntry {
  protocol_id: string;
  day_number: number;
  symptoms: string[];
  energy_level?: number;
  notes?: string;
}

export interface NexusResponse {
  module: string;
  recommendation: string;
  action_items: string[];
  references: string[];
  confidence?: number;
}

export interface NexusChatResponse {
  response: string;
  domain: string;
  intent: string;
  session_id: string | null;
  engine: string;
}

export interface VoiceChatResponse {
  transcript: string;
  response_text: string;
  audio_b64: string | null;   // base64 MP3 from server TTS
  domain: string;
  intent: string;
  session_id: string | null;
  tts_available: boolean;
}

export interface VoiceConfig {
  stt_available: boolean;
  tts_available: boolean;
  available_voices: string[];
  default_voice: string;
  default_speed?: number;
  supported_formats: string[];
  max_audio_mb: number;
}

// ── Media types ───────────────────────────────────────────────────────────────

export interface MediaConfig {
  dalle_available: boolean;
  openai_video_available?: boolean;
  music_available?: boolean;
  guides_available: boolean;
  fallback_images: boolean;
  supported_sizes: string[];
  supported_styles?: string[];
  guide_count: number;
  providers?: MediaProviderCapability[];
}

export interface MediaProviderCapability {
  id: string;
  label: string;
  media_type: "image" | "video" | "music";
  configured: boolean;
  model: string;
  status: string;
  note: string;
}

export interface MediaProviderJob {
  configured: boolean;
  provider: string;
  status: string;
  message?: string;
  video?: Record<string, unknown>;
  music?: Record<string, unknown>;
  request?: Record<string, unknown>;
}

export interface MediaImage {
  url: string;
  source: "dalle-3" | "gpt-image-1" | "unsplash" | "local" | string;
  prompt: string | null;
  revised_prompt: string | null;
  dalle_available: boolean;
}

export interface MediaGuideStep {
  step_number: number;
  title: string;
  description: string;
  action: string;
  icon: string;
  image: MediaImage;
}

export interface MediaGuide {
  id: string;
  title: string;
  subtitle: string;
  total_steps: number;
  steps: MediaGuideStep[];
  images_generated: boolean;
}

export interface MediaGuideInfo {
  id: string;
  title: string;
  subtitle: string;
  step_count: number;
}

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

export interface MediaQueryResult {
  type: "image" | "guide" | "guide_list" | "video" | "music";
  data: MediaImage | MediaGuide | MediaGuideInfo[] | MediaVideo | MediaProviderJob;
}

export interface MeatSubBase {
  id: string;
  name: string;
  protein_per_100g: number;
  texture: string;
  best_for: string[];
  prep: string;
  flavor_profile: string;
  nutrition_notes: string;
  craving_it_satisfies: string;
}

export interface MeatSubRecipe {
  id: string;
  name: string;
  satisfies_craving: string;
  base_ingredient: string;
  prep_time_min: number;
  cook_time_min: number;
  servings: number;
  difficulty: string;
  ingredients: string[];
  instructions: string[];
  pro_tips: string[];
  nutrition_per_serving: { calories: number; protein_g: number; fiber_g: number; fat_g: number };
  upgrade: string;
}

export interface MeatSubTechnique {
  technique: string;
  purpose: string;
  applies_to: string[];
  how: string;
  why_it_works: string;
}

export interface MeatSubForMeat {
  meat_type: string;
  substitutes: MeatSubBase[];
  recipes: MeatSubRecipe[];
}

// ── Food Medicine ─────────────────────────────────────────────────────────────

export interface HealingFoodItem {
  food: string;
  reason: string;
  evidence: string;
}

export interface SymptomAnalysis {
  condition: string;
  deficiencies: string[];
  excesses: string[];
  root_causes: string[];
  healing_foods: HealingFoodItem[];
  avoid: string[];
  protocol: string;
  nexus_insight: string | null;
}

export const foodMedicine = {
  analyse: (symptoms: string[], include_nexus = true) =>
    request<SymptomAnalysis[]>("/food-medicine/analyse", {
      method: "POST",
      body: JSON.stringify({ symptoms, include_nexus }),
    }),
  conditions: () =>
    request<{ conditions: { key: string; label: string }[] }>("/food-medicine/conditions"),
  condition: (key: string) =>
    request<SymptomAnalysis & { condition: string }>(`/food-medicine/condition/${key}`),
};

// ── Body Profile ──────────────────────────────────────────────────────────────

export interface PhysicalProfileData {
  height_cm?: number;
  weight_kg?: number;
  age?: number;
  biological_sex?: string;
  body_fat_pct?: number;
  waist_cm?: number;
  hip_cm?: number;
  resting_heart_rate?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  fasting_glucose?: number;
  activity_level?: string;
  exercise_days_per_week?: number;
  sleep_hours?: number;
  smoker?: boolean;
  alcohol_units_per_week?: number;
  water_litres_per_day?: number;
  medications?: string[];
  diagnosed_conditions?: string[];
  family_history?: string[];
  diet_type?: string;
  meal_frequency?: number;
  intermittent_fasting?: boolean;
}

export interface PsychProfileData {
  openness?: number;
  conscientiousness?: number;
  extraversion?: number;
  agreeableness?: number;
  neuroticism?: number;
  stress_level?: number;
  anxiety_level?: number;
  mood_stability?: number;
  motivation_level?: number;
  self_esteem?: number;
  mindfulness_practice?: boolean;
  social_connection?: number;
  purpose_clarity?: number;
  trauma_history?: boolean;
  therapy_current?: boolean;
  cognitive_load?: number;
  creativity_level?: number;
  primary_mental_goal?: string;
  biggest_mental_challenge?: string;
}

export interface BodyProfileAnalysis {
  body_metrics: {
    bmi?: number;
    bmi_category?: string;
    bmr_kcal?: number;
    tdee_kcal?: number;
    waist_hip_ratio?: number;
    whr_risk?: string;
    heart_rate_category?: string;
  };
  psych_metrics: {
    big_five?: Record<string, number>;
    resilience_index?: number;
    mental_health_snapshot?: Record<string, number>;
    overall_mental_wellness?: number;
  };
  nexus_analysis: string | null;
}

export const bodyProfile = {
  analyse: (physical: PhysicalProfileData, psychological: PsychProfileData) =>
    request<BodyProfileAnalysis>("/body-profile/analyse", {
      method: "POST",
      body: JSON.stringify({ physical, psychological }),
    }),
  questions: () =>
    request<{ physical_sections: unknown[]; psychological_sections: unknown[] }>("/body-profile/questions"),
};

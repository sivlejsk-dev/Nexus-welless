"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { bodyProfile, PhysicalProfileData, PsychProfileData, BodyProfileAnalysis } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Activity, Brain, ChevronLeft, ChevronRight, Sparkles,
  User, Heart, Clipboard, Target, BarChart3, CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ── Markdown renderer ─────────────────────────────────────────────────────────

function NexusMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
      p:      ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed text-white/75 text-sm">{children}</p>,
      strong: ({ children }) => <strong className="text-white/95 font-semibold">{children}</strong>,
      ul:     ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2 text-white/70 text-sm">{children}</ul>,
      ol:     ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2 text-white/70 text-sm">{children}</ol>,
      li:     ({ children }) => <li className="leading-relaxed">{children}</li>,
      h2:     ({ children }) => <h2 className="text-white font-semibold text-sm mb-1.5 mt-3">{children}</h2>,
      h3:     ({ children }) => <h3 className="text-white/90 font-medium text-sm mb-1 mt-2">{children}</h3>,
    }}>
      {content}
    </ReactMarkdown>
  );
}

// ── Step definitions ──────────────────────────────────────────────────────────

const STEPS = [
  { id: "body",        label: "Body",        icon: User,      color: "text-violet-400"  },
  { id: "vitals",      label: "Vitals",      icon: Heart,     color: "text-rose-400"    },
  { id: "lifestyle",   label: "Lifestyle",   icon: Activity,  color: "text-emerald-400" },
  { id: "medical",     label: "Medical",     icon: Clipboard, color: "text-amber-400"   },
  { id: "personality", label: "Personality", icon: Brain,     color: "text-sky-400"     },
  { id: "mental",      label: "Mental",      icon: Target,    color: "text-indigo-400"  },
];

const ACTIVITY_OPTIONS = ["sedentary", "light", "moderate", "active", "athlete"];
const SEX_OPTIONS      = ["male", "female", "other"];
const DIET_OPTIONS     = ["omnivore", "vegetarian", "vegan", "paleo", "keto", "mediterranean", "other"];

// ── Reusable field components ─────────────────────────────────────────────────

function FieldLabel({ label, optional }: { label: string; optional?: boolean }) {
  return (
    <label className="block text-white/60 text-xs font-medium mb-1.5">
      {label}
      {optional && <span className="ml-1 text-white/25 text-[10px]">(optional)</span>}
    </label>
  );
}

function NumberInput({ label, value, onChange, unit, optional, placeholder }: {
  label: string; value: number | undefined; onChange: (v: number | undefined) => void;
  unit?: string; optional?: boolean; placeholder?: string;
}) {
  return (
    <div>
      <FieldLabel label={label} optional={optional} />
      <div className="relative">
        <input
          type="number"
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
          placeholder={placeholder ?? "—"}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/40 transition-colors"
        />
        {unit && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 text-xs">{unit}</span>}
      </div>
    </div>
  );
}

function SelectInput({ label, value, onChange, options, optional }: {
  label: string; value: string | undefined; onChange: (v: string) => void;
  options: string[]; optional?: boolean;
}) {
  return (
    <div>
      <FieldLabel label={label} optional={optional} />
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500/40 transition-colors appearance-none"
      >
        <option value="" className="bg-gray-900">Select…</option>
        {options.map((o) => <option key={o} value={o} className="bg-gray-900 capitalize">{o}</option>)}
      </select>
    </div>
  );
}

function BooleanToggle({ label, value, onChange }: {
  label: string; value: boolean | undefined; onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-white/60 text-sm">{label}</span>
      <div className="flex gap-2">
        {[true, false].map((v) => (
          <button key={String(v)} onClick={() => onChange(v)}
            className={cn(
              "px-3 py-1 rounded-lg text-xs font-medium transition-all border",
              value === v
                ? "bg-violet-600/30 border-violet-500/40 text-violet-300"
                : "bg-white/5 border-white/10 text-white/40 hover:text-white/70"
            )}>
            {v ? "Yes" : "No"}
          </button>
        ))}
      </div>
    </div>
  );
}

function SliderInput({ label, value, onChange, description }: {
  label: string; value: number | undefined; onChange: (v: number) => void; description?: string;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <FieldLabel label={label} />
        <span className="text-violet-400 text-sm font-bold tabular-nums">{value ?? "—"}</span>
      </div>
      {description && <p className="text-white/30 text-[11px]">{description}</p>}
      <input
        type="range" min={1} max={10} step={1}
        value={value ?? 5}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-violet-500 cursor-pointer"
      />
      <div className="flex justify-between text-white/20 text-[10px]">
        <span>1</span><span>5</span><span>10</span>
      </div>
    </div>
  );
}

function TagsInput({ label, value, onChange }: {
  label: string; value: string[]; onChange: (v: string[]) => void;
}) {
  const [input, setInput] = useState("");
  const add = () => {
    const clean = input.trim();
    if (clean && !value.includes(clean)) onChange([...value, clean]);
    setInput("");
  };
  return (
    <div>
      <FieldLabel label={label} optional />
      <div className="flex gap-2 mb-2">
        <input
          type="text" value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          placeholder="Type and press Enter…"
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/40 transition-colors"
        />
        <Button size="sm" onClick={add} disabled={!input.trim()}>Add</Button>
      </div>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {value.map((v) => (
            <span key={v} className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-violet-500/10 border border-violet-500/20 text-violet-300">
              {v}
              <button onClick={() => onChange(value.filter((x) => x !== v))} className="hover:text-white ml-0.5">×</button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Metric card ───────────────────────────────────────────────────────────────

function MetricCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="bg-white/4 border border-white/8 rounded-xl p-4 space-y-1">
      <p className="text-white/40 text-xs uppercase tracking-wider">{label}</p>
      <p className={cn("text-2xl font-bold", color ?? "text-white")}>{value}</p>
      {sub && <p className="text-white/40 text-xs">{sub}</p>}
    </div>
  );
}

// ── Results view ──────────────────────────────────────────────────────────────

function ResultsView({ analysis, onReset }: { analysis: BodyProfileAnalysis; onReset: () => void }) {
  const bm = analysis.body_metrics;
  const pm = analysis.psych_metrics;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-white font-bold text-xl">Your Wellness Profile</h2>
          <p className="text-white/40 text-sm mt-0.5">Personalised analysis from Nexus AI</p>
        </div>
        <Button variant="secondary" size="sm" onClick={onReset}>
          <User className="w-3.5 h-3.5 mr-1.5" /> New Profile
        </Button>
      </div>

      {/* Body metrics */}
      {Object.keys(bm).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Activity className="w-4 h-4 text-violet-400" /> Body Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {bm.bmi !== undefined && (
                <MetricCard label="BMI" value={bm.bmi}
                  sub={bm.bmi_category}
                  color={bm.bmi_category === "Normal" ? "text-emerald-400" : bm.bmi_category === "Underweight" ? "text-sky-400" : "text-amber-400"} />
              )}
              {bm.bmr_kcal !== undefined && <MetricCard label="BMR" value={`${bm.bmr_kcal} kcal`} sub="Base metabolic rate" color="text-violet-400" />}
              {bm.tdee_kcal !== undefined && <MetricCard label="TDEE" value={`${bm.tdee_kcal} kcal`} sub="Daily energy need" color="text-indigo-400" />}
              {bm.waist_hip_ratio !== undefined && (
                <MetricCard label="Waist/Hip Ratio" value={bm.waist_hip_ratio}
                  sub={bm.whr_risk ? `${bm.whr_risk} risk` : undefined}
                  color={bm.whr_risk === "Low" ? "text-emerald-400" : bm.whr_risk === "Moderate" ? "text-amber-400" : "text-rose-400"} />
              )}
              {bm.heart_rate_category && <MetricCard label="Resting HR" value={bm.heart_rate_category} color="text-rose-400" />}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Psych metrics */}
      {Object.keys(pm).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Brain className="w-4 h-4 text-sky-400" /> Mental Wellness
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {pm.overall_mental_wellness !== undefined && (
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-sky-400 text-2xl font-bold">{pm.overall_mental_wellness}</span>
                </div>
                <div>
                  <p className="text-white font-semibold">Overall Mental Wellness</p>
                  <p className="text-white/40 text-sm">Score out of 10</p>
                </div>
              </div>
            )}
            {pm.resilience_index !== undefined && (
              <div className="bg-indigo-500/8 border border-indigo-500/15 rounded-xl p-3 flex items-center justify-between">
                <span className="text-white/60 text-sm">Resilience Index</span>
                <span className="text-indigo-400 font-bold">{pm.resilience_index} / 10</span>
              </div>
            )}
            {pm.big_five && (
              <div>
                <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Big Five Personality</p>
                <div className="space-y-2">
                  {Object.entries(pm.big_five).map(([trait, score]) => (
                    <div key={trait} className="flex items-center gap-3">
                      <span className="text-white/50 text-xs w-28 capitalize">{trait}</span>
                      <div className="flex-1 h-1.5 bg-white/8 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all"
                          style={{ width: `${(score / 10) * 100}%` }} />
                      </div>
                      <span className="text-white/60 text-xs tabular-nums w-4">{score}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Nexus AI analysis */}
      {analysis.nexus_analysis && (
        <div className="bg-gradient-to-r from-violet-500/8 to-indigo-500/8 border border-violet-500/15 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <p className="text-violet-300 text-sm font-semibold uppercase tracking-wider">Nexus Personalised Assessment</p>
          </div>
          <NexusMarkdown content={analysis.nexus_analysis} />
        </div>
      )}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function BodyProfilePage() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BodyProfileAnalysis | null>(null);

  // Physical state
  const [physical, setPhysical] = useState<PhysicalProfileData>({
    medications: [], diagnosed_conditions: [], family_history: [],
  });
  // Psychological state
  const [psych, setPsych] = useState<PsychProfileData>({});

  const setP = (k: keyof PhysicalProfileData, v: unknown) =>
    setPhysical((prev) => ({ ...prev, [k]: v }));
  const setPsy = (k: keyof PsychProfileData, v: unknown) =>
    setPsych((prev) => ({ ...prev, [k]: v }));

  const submit = async () => {
    setLoading(true);
    try {
      const data = await bodyProfile.analyse(physical, psych);
      setResult(data);
    } catch {
      // keep form visible on error
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setStep(0);
    setPhysical({ medications: [], diagnosed_conditions: [], family_history: [] });
    setPsych({});
  };

  if (result) return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-7 h-7 text-violet-400" /> Body Profile
        </h1>
        <p className="text-white/40 mt-1">Your complete physical and psychological wellness assessment.</p>
      </div>
      <ResultsView analysis={result} onReset={reset} />
    </div>
  );

  const isLast = step === STEPS.length - 1;
  const currentStep = STEPS[step];
  const StepIcon = currentStep.icon;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-7 h-7 text-violet-400" /> Body Profile
        </h1>
        <p className="text-white/40 mt-1">
          Complete your physical and psychological profile for a personalised Nexus wellness assessment.
        </p>
      </div>

      {/* Nexus intro */}
      <NexusInsight
        context="body profile"
        prompt="In 2 sentences, explain why understanding both physical metrics and psychological profile together gives a far more accurate wellness picture than either alone."
        accentClass="bg-violet-500/15 text-violet-400"
        lazy
      />

      {/* Step progress */}
      <div className="flex items-center gap-1.5">
        {STEPS.map((s, i) => {
          const Icon = s.icon;
          return (
            <button key={s.id} onClick={() => setStep(i)}
              className={cn(
                "flex-1 flex flex-col items-center gap-1 py-2 rounded-xl transition-all text-[10px] font-medium",
                i === step ? "bg-white/8 text-white" : i < step ? "text-white/50" : "text-white/20"
              )}>
              <Icon className={cn("w-3.5 h-3.5", i === step ? s.color : i < step ? "text-white/40" : "text-white/15")} />
              <span className="hidden sm:block">{s.label}</span>
              {i < step && <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400 hidden sm:block" />}
            </button>
          );
        })}
      </div>

      {/* Step card */}
      <Card>
        <CardHeader>
          <CardTitle className={cn("flex items-center gap-2", currentStep.color)}>
            <StepIcon className="w-4 h-4" />
            {step === 0 && "Body Measurements"}
            {step === 1 && "Vital Signs"}
            {step === 2 && "Lifestyle"}
            {step === 3 && "Medical History"}
            {step === 4 && "Personality Profile"}
            {step === 5 && "Mental Wellness"}
          </CardTitle>
          <p className="text-white/30 text-xs mt-1">
            Step {step + 1} of {STEPS.length}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">

          {/* Step 0 — Body */}
          {step === 0 && (
            <>
              <div className="grid sm:grid-cols-2 gap-4">
                <NumberInput label="Height" value={physical.height_cm} onChange={(v) => setP("height_cm", v)} unit="cm" />
                <NumberInput label="Weight" value={physical.weight_kg} onChange={(v) => setP("weight_kg", v)} unit="kg" />
                <NumberInput label="Age" value={physical.age} onChange={(v) => setP("age", v)} />
                <SelectInput label="Biological Sex" value={physical.biological_sex} onChange={(v) => setP("biological_sex", v)} options={SEX_OPTIONS} />
                <NumberInput label="Body Fat %" value={physical.body_fat_pct} onChange={(v) => setP("body_fat_pct", v)} unit="%" optional />
                <NumberInput label="Waist circumference" value={physical.waist_cm} onChange={(v) => setP("waist_cm", v)} unit="cm" optional />
                <NumberInput label="Hip circumference" value={physical.hip_cm} onChange={(v) => setP("hip_cm", v)} unit="cm" optional />
              </div>
            </>
          )}

          {/* Step 1 — Vitals */}
          {step === 1 && (
            <div className="grid sm:grid-cols-2 gap-4">
              <NumberInput label="Resting Heart Rate" value={physical.resting_heart_rate} onChange={(v) => setP("resting_heart_rate", v)} unit="bpm" optional />
              <NumberInput label="Systolic BP" value={physical.systolic_bp} onChange={(v) => setP("systolic_bp", v)} unit="mmHg" optional />
              <NumberInput label="Diastolic BP" value={physical.diastolic_bp} onChange={(v) => setP("diastolic_bp", v)} unit="mmHg" optional />
              <NumberInput label="Fasting Glucose" value={physical.fasting_glucose} onChange={(v) => setP("fasting_glucose", v)} unit="mmol/L" optional />
            </div>
          )}

          {/* Step 2 — Lifestyle */}
          {step === 2 && (
            <div className="space-y-4">
              <SelectInput label="Activity Level" value={physical.activity_level} onChange={(v) => setP("activity_level", v)} options={ACTIVITY_OPTIONS} />
              <div className="grid sm:grid-cols-2 gap-4">
                <NumberInput label="Exercise days/week" value={physical.exercise_days_per_week} onChange={(v) => setP("exercise_days_per_week", v)} />
                <NumberInput label="Sleep hours/night" value={physical.sleep_hours} onChange={(v) => setP("sleep_hours", v)} unit="hrs" />
                <NumberInput label="Water intake" value={physical.water_litres_per_day} onChange={(v) => setP("water_litres_per_day", v)} unit="L/day" optional />
                <NumberInput label="Alcohol units/week" value={physical.alcohol_units_per_week} onChange={(v) => setP("alcohol_units_per_week", v)} optional />
              </div>
              <BooleanToggle label="Do you smoke?" value={physical.smoker} onChange={(v) => setP("smoker", v)} />
              <BooleanToggle label="Intermittent fasting?" value={physical.intermittent_fasting} onChange={(v) => setP("intermittent_fasting", v)} />
            </div>
          )}

          {/* Step 3 — Medical */}
          {step === 3 && (
            <div className="space-y-4">
              <SelectInput label="Diet type" value={physical.diet_type} onChange={(v) => setP("diet_type", v)} options={DIET_OPTIONS} optional />
              <NumberInput label="Meals per day" value={physical.meal_frequency} onChange={(v) => setP("meal_frequency", v)} optional />
              <TagsInput label="Diagnosed conditions" value={physical.diagnosed_conditions ?? []} onChange={(v) => setP("diagnosed_conditions", v)} />
              <TagsInput label="Current medications" value={physical.medications ?? []} onChange={(v) => setP("medications", v)} />
              <TagsInput label="Family health history" value={physical.family_history ?? []} onChange={(v) => setP("family_history", v)} />
            </div>
          )}

          {/* Step 4 — Personality */}
          {step === 4 && (
            <div className="space-y-5">
              <p className="text-white/30 text-xs">Rate yourself 1 (low) to 10 (high)</p>
              <SliderInput label="Openness" value={psych.openness} onChange={(v) => setPsy("openness", v)} description="Curiosity, creativity, willingness to try new things" />
              <SliderInput label="Conscientiousness" value={psych.conscientiousness} onChange={(v) => setPsy("conscientiousness", v)} description="Organisation, discipline, goal-directedness" />
              <SliderInput label="Extraversion" value={psych.extraversion} onChange={(v) => setPsy("extraversion", v)} description="Sociability, assertiveness, positive emotions" />
              <SliderInput label="Agreeableness" value={psych.agreeableness} onChange={(v) => setPsy("agreeableness", v)} description="Compassion, cooperation, trust in others" />
              <SliderInput label="Emotional reactivity" value={psych.neuroticism} onChange={(v) => setPsy("neuroticism", v)} description="Tendency to experience negative emotions" />
            </div>
          )}

          {/* Step 5 — Mental */}
          {step === 5 && (
            <div className="space-y-5">
              <SliderInput label="Current stress level" value={psych.stress_level} onChange={(v) => setPsy("stress_level", v)} description="1 = very calm, 10 = extremely stressed" />
              <SliderInput label="Anxiety level" value={psych.anxiety_level} onChange={(v) => setPsy("anxiety_level", v)} description="1 = no anxiety, 10 = severe anxiety" />
              <SliderInput label="Mood stability" value={psych.mood_stability} onChange={(v) => setPsy("mood_stability", v)} description="1 = very unstable, 10 = very stable" />
              <SliderInput label="Motivation & drive" value={psych.motivation_level} onChange={(v) => setPsy("motivation_level", v)} description="1 = no motivation, 10 = highly motivated" />
              <SliderInput label="Self-esteem" value={psych.self_esteem} onChange={(v) => setPsy("self_esteem", v)} description="1 = very low, 10 = very high" />
              <SliderInput label="Social connection" value={psych.social_connection} onChange={(v) => setPsy("social_connection", v)} description="1 = very isolated, 10 = deeply connected" />
              <SliderInput label="Sense of purpose" value={psych.purpose_clarity} onChange={(v) => setPsy("purpose_clarity", v)} description="1 = no direction, 10 = crystal clear purpose" />
              <div className="space-y-3 pt-2 border-t border-white/8">
                <BooleanToggle label="Do you have a mindfulness practice?" value={psych.mindfulness_practice} onChange={(v) => setPsy("mindfulness_practice", v)} />
                <BooleanToggle label="Currently in therapy?" value={psych.therapy_current} onChange={(v) => setPsy("therapy_current", v)} />
                <BooleanToggle label="Significant trauma history?" value={psych.trauma_history} onChange={(v) => setPsy("trauma_history", v)} />
              </div>
              <div>
                <FieldLabel label="Primary mental health goal" />
                <input type="text" value={psych.primary_mental_goal ?? ""}
                  onChange={(e) => setPsy("primary_mental_goal", e.target.value)}
                  placeholder="e.g. reduce anxiety, improve focus, build confidence"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/40 transition-colors" />
              </div>
              <div>
                <FieldLabel label="Biggest mental challenge right now" />
                <input type="text" value={psych.biggest_mental_challenge ?? ""}
                  onChange={(e) => setPsy("biggest_mental_challenge", e.target.value)}
                  placeholder="e.g. overthinking, low energy, relationship stress"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/40 transition-colors" />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex gap-3">
        {step > 0 && (
          <Button variant="secondary" onClick={() => setStep((s) => s - 1)} className="flex-1">
            <ChevronLeft className="w-4 h-4 mr-1" /> Back
          </Button>
        )}
        {!isLast ? (
          <Button onClick={() => setStep((s) => s + 1)} className="flex-1">
            Next <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        ) : (
          <Button onClick={submit} disabled={loading} className="flex-1">
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analysing with Nexus AI…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Generate My Assessment
              </span>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

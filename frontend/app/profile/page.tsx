"use client";

import { useEffect, useState } from "react";
import { users, WellnessProfile } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { User, Save, X, LogOut, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const GOAL_OPTIONS = [
  "weight-loss","stress-relief","better-sleep","detox","energy",
  "gut-health","spiritual-growth","anti-aging","muscle-gain","mental-clarity",
];
const DIET_OPTIONS = [
  "vegan","vegetarian","paleo","keto","gluten-free",
  "dairy-free","raw-food","mediterranean","whole-food","low-sugar",
];
const CONDITION_OPTIONS = [
  "anxiety","depression","ibs","inflammation","diabetes",
  "hypertension","autoimmune","thyroid","hormonal","chronic-fatigue",
];
const ALLERGY_OPTIONS = [
  "gluten","dairy","nuts","soy","eggs","shellfish","nightshades","corn",
];

function TagPicker({
  label, options, selected, onToggle, variant = "violet",
}: {
  label: string;
  options: string[];
  selected: string[];
  onToggle: (item: string) => void;
  variant?: "violet" | "emerald" | "rose" | "amber";
}) {
  const colors: Record<string, string> = {
    violet:  "bg-violet-600 text-white",
    emerald: "bg-emerald-600 text-white",
    rose:    "bg-rose-600 text-white",
    amber:   "bg-amber-600 text-white",
  };
  return (
    <div>
      <p className="text-white/40 text-xs uppercase tracking-wider mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((o) => {
          const active = selected.includes(o);
          return (
            <button key={o} onClick={() => onToggle(o)}
              className={cn("px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1",
                active ? colors[variant] : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10")}>
              {active && <X className="w-3 h-3" />}
              {o}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<WellnessProfile>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showNexus, setShowNexus] = useState(false);

  useEffect(() => { users.getProfile().then(setProfile).catch(() => {}); }, []);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await users.updateProfile(profile);
      setProfile(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } finally { setSaving(false); }
  };

  const toggleItem = (field: "health_goals" | "dietary_preferences" | "allergies" | "conditions", item: string) => {
    const current = profile[field] ?? [];
    setProfile((p) => ({
      ...p,
      [field]: current.includes(item) ? current.filter((i) => i !== item) : [...current, item],
    }));
  };

  const handleLogout = () => { logout(); router.push("/login"); };

  const nexusPrompt = [
    profile.health_goals?.length ? `Health goals: ${profile.health_goals.join(", ")}.` : "",
    profile.dietary_preferences?.length ? `Diet: ${profile.dietary_preferences.join(", ")}.` : "",
    profile.conditions?.length ? `Conditions: ${profile.conditions.join(", ")}.` : "",
    profile.sun_sign ? `Sun sign: ${profile.sun_sign}.` : "",
  ].filter(Boolean).join(" ") || "I haven't set up my profile yet.";

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <User className="w-7 h-7 text-white/60" /> Wellness Profile
          </h1>
          <p className="text-white/40 mt-1">Your profile powers Nexus AI personalization.</p>
        </div>
        <button onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 hover:bg-rose-500/15 text-white/40 hover:text-rose-400 text-sm transition-all">
          <LogOut className="w-4 h-4" /> Sign out
        </button>
      </div>

      {/* Account */}
      <Card>
        <CardHeader><CardTitle>Account</CardTitle></CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-white/90 font-medium">{user?.full_name ?? "—"}</p>
              <p className="text-white/40 text-sm">{user?.email}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Birth & Location */}
      <Card>
        <CardHeader><CardTitle>Birth Details</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Date of Birth",  field: "date_of_birth",   type: "date",   placeholder: undefined,          colSpan: false },
              { label: "Birth Time",     field: "birth_time",      type: "time",   placeholder: "HH:MM",            colSpan: false },
              { label: "Birth Location", field: "birth_location",  type: "text",   placeholder: "City, Country",    colSpan: true  },
              { label: "Timezone",       field: "timezone",        type: "text",   placeholder: "e.g. America/New_York", colSpan: false },
            ].map(({ label, field, type, placeholder, colSpan }) => (
              <div key={field} className={colSpan ? "col-span-2" : ""}>
                <label className="block text-white/40 text-xs mb-1.5">{label}</label>
                <input type={type}
                  value={(profile[field as keyof WellnessProfile] as string) ?? ""}
                  onChange={(e) => setProfile((p) => ({ ...p, [field]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/50 transition-colors" />
              </div>
            ))}
          </div>
          {(profile.sun_sign || profile.moon_sign || profile.rising_sign) && (
            <div className="flex gap-2 mt-4 pt-4 border-t border-white/5 flex-wrap">
              {profile.sun_sign   && <Badge variant="amber">☀️ {profile.sun_sign}</Badge>}
              {profile.moon_sign  && <Badge variant="violet">🌙 {profile.moon_sign}</Badge>}
              {profile.rising_sign && <Badge variant="sky">⬆️ {profile.rising_sign}</Badge>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Body Metrics */}
      <Card>
        <CardHeader><CardTitle>Body Metrics</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Height (cm)", field: "height_cm" },
              { label: "Weight (kg)", field: "weight_kg" },
            ].map(({ label, field }) => (
              <div key={field}>
                <label className="block text-white/40 text-xs mb-1.5">{label}</label>
                <input type="number"
                  value={(profile[field as keyof WellnessProfile] as number) ?? ""}
                  onChange={(e) => setProfile((p) => ({ ...p, [field]: parseFloat(e.target.value) || undefined }))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500/50 transition-colors" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Health Goals */}
      <Card>
        <CardHeader><CardTitle>Health Goals</CardTitle></CardHeader>
        <CardContent>
          <TagPicker label="" options={GOAL_OPTIONS} selected={profile.health_goals ?? []}
            onToggle={(item) => toggleItem("health_goals", item)} variant="violet" />
        </CardContent>
      </Card>

      {/* Dietary Preferences */}
      <Card>
        <CardHeader><CardTitle>Dietary Preferences</CardTitle></CardHeader>
        <CardContent>
          <TagPicker label="" options={DIET_OPTIONS} selected={profile.dietary_preferences ?? []}
            onToggle={(item) => toggleItem("dietary_preferences", item)} variant="emerald" />
        </CardContent>
      </Card>

      {/* Health Conditions */}
      <Card>
        <CardHeader><CardTitle>Health Conditions</CardTitle></CardHeader>
        <CardContent>
          <p className="text-white/30 text-xs mb-3">Nexus uses this to personalise recommendations. This data stays private.</p>
          <TagPicker label="" options={CONDITION_OPTIONS} selected={profile.conditions ?? []}
            onToggle={(item) => toggleItem("conditions", item)} variant="amber" />
        </CardContent>
      </Card>

      {/* Allergies */}
      <Card>
        <CardHeader><CardTitle>Allergies & Sensitivities</CardTitle></CardHeader>
        <CardContent>
          <TagPicker label="" options={ALLERGY_OPTIONS} selected={profile.allergies ?? []}
            onToggle={(item) => toggleItem("allergies", item)} variant="rose" />
        </CardContent>
      </Card>

      {/* Save */}
      <Button onClick={save} disabled={saving} size="lg" className="w-full">
        <Save className="w-4 h-4 mr-2" />
        {saving ? "Saving…" : saved ? "✓ Saved" : "Save Profile"}
      </Button>

      {/* Nexus personalisation summary */}
      <div>
        <button onClick={() => setShowNexus((v) => !v)}
          className={cn("w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm transition-all",
            showNexus ? "bg-violet-500/15 text-violet-300" : "text-white/30 hover:text-white/60 hover:bg-white/5")}>
          <Sparkles className="w-4 h-4" />
          {showNexus ? "Hide Nexus analysis" : "Get Nexus to analyse my profile"}
        </button>
        {showNexus && (
          <div className="mt-3">
            <NexusInsight
              context="wellness profile"
              prompt={`Based on my wellness profile: ${nexusPrompt} — give me a personalised wellness analysis. What are my key priorities, what should I focus on first, and what does Nexus recommend as my top 3 action steps?`}
              accentClass="bg-violet-500/15 text-violet-400"
            />
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { users, WellnessProfile } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { User, Save, Plus, X } from "lucide-react";

const GOAL_OPTIONS = ["weight-loss", "stress-relief", "better-sleep", "detox", "energy", "gut-health", "spiritual-growth", "anti-aging"];
const DIET_OPTIONS = ["vegan", "vegetarian", "paleo", "keto", "gluten-free", "dairy-free", "raw-food", "mediterranean"];

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<WellnessProfile>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    users.getProfile().then(setProfile).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await users.updateProfile(profile);
      setProfile(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  const toggleItem = (field: "health_goals" | "dietary_preferences" | "allergies" | "conditions", item: string) => {
    const current = profile[field] ?? [];
    const next = current.includes(item) ? current.filter((i) => i !== item) : [...current, item];
    setProfile((p) => ({ ...p, [field]: next }));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <User className="w-7 h-7 text-white/60" /> Wellness Profile
        </h1>
        <p className="text-white/40 mt-1">Your profile powers Nexus AI personalization.</p>
      </div>

      {/* Account */}
      <Card>
        <CardHeader><CardTitle>Account</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-1">
            <p className="text-white/80">{user?.full_name ?? "—"}</p>
            <p className="text-white/40 text-sm">{user?.email}</p>
          </div>
        </CardContent>
      </Card>

      {/* Birth & Location */}
      <Card>
        <CardHeader><CardTitle>Birth Details</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Date of Birth", field: "date_of_birth", type: "date" },
              { label: "Birth Time", field: "birth_time", type: "time", placeholder: "HH:MM" },
              { label: "Birth Location", field: "birth_location", type: "text", placeholder: "City, Country", colSpan: true },
              { label: "Timezone", field: "timezone", type: "text", placeholder: "e.g. America/New_York" },
            ].map(({ label, field, type, placeholder, colSpan }) => (
              <div key={field} className={colSpan ? "col-span-2" : ""}>
                <label className="block text-white/40 text-xs mb-1.5">{label}</label>
                <input
                  type={type}
                  value={(profile[field as keyof WellnessProfile] as string) ?? ""}
                  onChange={(e) => setProfile((p) => ({ ...p, [field]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/50 transition-colors"
                />
              </div>
            ))}
          </div>
          {profile.sun_sign && (
            <div className="flex gap-2 mt-4 pt-4 border-t border-white/5">
              <Badge variant="amber">☀️ {profile.sun_sign}</Badge>
              {profile.moon_sign && <Badge variant="violet">🌙 {profile.moon_sign}</Badge>}
              {profile.rising_sign && <Badge variant="sky">⬆️ {profile.rising_sign}</Badge>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Body */}
      <Card>
        <CardHeader><CardTitle>Body Metrics</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Height (cm)", field: "height_cm", type: "number" },
              { label: "Weight (kg)", field: "weight_kg", type: "number" },
            ].map(({ label, field, type }) => (
              <div key={field}>
                <label className="block text-white/40 text-xs mb-1.5">{label}</label>
                <input
                  type={type}
                  value={(profile[field as keyof WellnessProfile] as number) ?? ""}
                  onChange={(e) => setProfile((p) => ({ ...p, [field]: parseFloat(e.target.value) || undefined }))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500/50 transition-colors"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Health Goals */}
      <Card>
        <CardHeader><CardTitle>Health Goals</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {GOAL_OPTIONS.map((g) => {
              const active = profile.health_goals?.includes(g);
              return (
                <button
                  key={g}
                  onClick={() => toggleItem("health_goals", g)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1 ${
                    active ? "bg-violet-600 text-white" : "bg-white/5 text-white/50 hover:text-white"
                  }`}
                >
                  {active && <X className="w-3 h-3" />}
                  {g}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Dietary Preferences */}
      <Card>
        <CardHeader><CardTitle>Dietary Preferences</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {DIET_OPTIONS.map((d) => {
              const active = profile.dietary_preferences?.includes(d);
              return (
                <button
                  key={d}
                  onClick={() => toggleItem("dietary_preferences", d)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    active ? "bg-emerald-600 text-white" : "bg-white/5 text-white/50 hover:text-white"
                  }`}
                >
                  {d}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Button onClick={save} disabled={saving} size="lg" className="w-full">
        <Save className="w-4 h-4 mr-2" />
        {saving ? "Saving…" : saved ? "✓ Saved" : "Save Profile"}
      </Button>
    </div>
  );
}

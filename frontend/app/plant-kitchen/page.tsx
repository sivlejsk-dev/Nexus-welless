"use client";

import { useEffect, useState } from "react";
import { meatSubs, MeatSubBase, MeatSubRecipe, MeatSubTechnique } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Leaf, ChefHat, Zap, Search, Clock, Users, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

const MEAT_TYPES = ["beef", "chicken", "bacon", "fish", "pork", "steak", "tuna", "burger"];
const TABS = ["recipes", "bases", "techniques"] as const;
type Tab = typeof TABS[number];

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "text-emerald-400 bg-emerald-400/10",
  medium: "text-amber-400 bg-amber-400/10",
  advanced: "text-rose-400 bg-rose-400/10",
};

export default function PlantKitchenPage() {
  const [tab, setTab] = useState<Tab>("recipes");
  const [recipes, setRecipes] = useState<MeatSubRecipe[]>([]);
  const [bases, setBases] = useState<MeatSubBase[]>([]);
  const [techniques, setTechniques] = useState<MeatSubTechnique[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [craving, setCraving] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTab(tab);
  }, [tab]);

  const loadTab = async (t: Tab) => {
    setLoading(true);
    try {
      if (t === "recipes" && recipes.length === 0) {
        const data = await meatSubs.recipes();
        setRecipes(Array.isArray(data) ? data : []);
      }
      if (t === "bases" && bases.length === 0) {
        setBases(await meatSubs.bases());
      }
      if (t === "techniques" && techniques.length === 0) {
        setTechniques(await meatSubs.techniques());
      }
    } finally {
      setLoading(false);
    }
  };

  const searchCraving = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setTab("recipes");
    try {
      const data = await meatSubs.forMeat(q);
      setRecipes(data.recipes);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-0">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <ChefHat className="w-7 h-7 text-emerald-400" /> Plant Kitchen
        </h1>
        <p className="text-white/40 mt-1">
          Satisfy every meat craving with plants — same textures, deeper nutrition.
        </p>
      </div>

      {/* Craving search */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-3">
        <p className="text-white/60 text-sm font-medium">What are you craving?</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={craving}
            onChange={(e) => setCraving(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchCraving(craving)}
            placeholder="e.g. bacon, burger, fried chicken, steak…"
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50"
          />
          <Button onClick={() => searchCraving(craving)} disabled={loading}>
            <Search className="w-4 h-4 mr-2" /> Find
          </Button>
        </div>
        <div className="flex gap-2 flex-wrap">
          {MEAT_TYPES.map((m) => (
            <button
              key={m}
              onClick={() => { setCraving(m); searchCraving(m); }}
              className="px-3 py-1 rounded-full text-xs font-medium bg-white/5 text-white/50 hover:text-white hover:bg-emerald-600/30 transition-all"
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/5 rounded-xl p-1">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "flex-1 py-2 rounded-lg text-sm font-medium transition-all capitalize",
              tab === t ? "bg-emerald-600 text-white" : "text-white/40 hover:text-white"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="rounded-2xl h-24 bg-white/5 animate-pulse" />)}
        </div>
      )}

      {/* Recipes tab */}
      {tab === "recipes" && !loading && (
        <div className="space-y-4">
          {recipes.length === 0 ? (
            <p className="text-white/30 text-center py-12">No recipes found. Try a different craving.</p>
          ) : (
            recipes.map((r) => (
              <Card key={r.id} className="cursor-pointer" onClick={() => setExpanded(expanded === r.id ? null : r.id)}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <CardTitle className="text-base">{r.name}</CardTitle>
                        <span className={cn("text-xs px-2 py-0.5 rounded-full font-medium", DIFFICULTY_COLORS[r.difficulty])}>
                          {r.difficulty}
                        </span>
                      </div>
                      <p className="text-white/40 text-xs mt-1">Satisfies: {r.satisfies_craving}</p>
                    </div>
                    {expanded === r.id ? <ChevronUp className="w-4 h-4 text-white/30 flex-shrink-0" /> : <ChevronDown className="w-4 h-4 text-white/30 flex-shrink-0" />}
                  </div>
                  <div className="flex gap-3 mt-2 text-white/40 text-xs">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{r.prep_time_min + r.cook_time_min} min</span>
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" />{r.servings} servings</span>
                    <span className="flex items-center gap-1"><Leaf className="w-3 h-3" />{r.base_ingredient}</span>
                    <span>{r.nutrition_per_serving.calories} kcal · {r.nutrition_per_serving.protein_g}g protein</span>
                  </div>
                </CardHeader>

                {expanded === r.id && (
                  <CardContent className="space-y-4 border-t border-white/5 pt-4">
                    {/* Ingredients */}
                    <div>
                      <p className="text-white/50 text-xs font-semibold uppercase tracking-wider mb-2">Ingredients</p>
                      <ul className="space-y-1">
                        {r.ingredients.map((ing, i) => (
                          <li key={i} className="text-white/70 text-sm flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0 mt-1.5" />
                            {ing}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Instructions */}
                    <div>
                      <p className="text-white/50 text-xs font-semibold uppercase tracking-wider mb-2">Instructions</p>
                      <ol className="space-y-2">
                        {r.instructions.map((step, i) => (
                          <li key={i} className="text-white/70 text-sm flex gap-3">
                            <span className="w-5 h-5 rounded-full bg-emerald-600/30 text-emerald-400 text-xs flex items-center justify-center flex-shrink-0 mt-0.5 font-bold">
                              {i + 1}
                            </span>
                            {step}
                          </li>
                        ))}
                      </ol>
                    </div>

                    {/* Pro tips */}
                    <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 space-y-1">
                      <p className="text-amber-400 text-xs font-semibold uppercase tracking-wider mb-2">Pro Tips</p>
                      {r.pro_tips.map((tip, i) => (
                        <p key={i} className="text-white/70 text-sm flex items-start gap-2">
                          <Zap className="w-3 h-3 text-amber-400 flex-shrink-0 mt-0.5" />
                          {tip}
                        </p>
                      ))}
                    </div>

                    {/* Upgrade */}
                    <div className="bg-violet-500/10 border border-violet-500/20 rounded-xl p-3">
                      <p className="text-violet-400 text-xs font-semibold uppercase tracking-wider mb-1">Level Up</p>
                      <p className="text-white/70 text-sm">{r.upgrade}</p>
                    </div>
                  </CardContent>
                )}
              </Card>
            ))
          )}
        </div>
      )}

      {/* Bases tab */}
      {tab === "bases" && !loading && (
        <div className="grid gap-4 sm:grid-cols-2">
          {bases.map((b) => (
            <Card key={b.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">{b.name}</CardTitle>
                  <Badge variant="emerald">{b.protein_per_100g}g protein</Badge>
                </div>
                <p className="text-white/40 text-xs mt-1 italic">{b.texture}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-white/40 text-xs mb-1">Best for</p>
                  <div className="flex flex-wrap gap-1">
                    {b.best_for.map((f) => <Badge key={f} variant="default">{f}</Badge>)}
                  </div>
                </div>
                <div>
                  <p className="text-white/40 text-xs mb-1">How to prep</p>
                  <p className="text-white/70 text-xs leading-relaxed">{b.prep}</p>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <p className="text-white/40 text-xs mb-0.5">Nutrition note</p>
                  <p className="text-white/60 text-xs">{b.nutrition_notes}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Techniques tab */}
      {tab === "techniques" && !loading && (
        <div className="space-y-4">
          {techniques.map((t) => (
            <Card key={t.technique}>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  {t.technique}
                </CardTitle>
                <p className="text-white/60 text-sm mt-1">{t.purpose}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-white/40 text-xs mb-1">How to do it</p>
                  <p className="text-white/70 text-sm">{t.how}</p>
                </div>
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                  <p className="text-emerald-400 text-xs font-medium mb-1">Why it works</p>
                  <p className="text-white/70 text-xs">{t.why_it_works}</p>
                </div>
                <div>
                  <p className="text-white/40 text-xs mb-1">Works with</p>
                  <div className="flex flex-wrap gap-1">
                    {t.applies_to.map((a) => <Badge key={a} variant="default">{a}</Badge>)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

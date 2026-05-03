"use client";

import { useEffect, useState } from "react";
import { nutrition, HealingFood, MealPlan } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Leaf, Search } from "lucide-react";
import { cn } from "@/lib/utils";

const CONDITIONS = ["inflammation", "gut-health", "stress", "detox", "energy", "sleep", "immunity"];

export default function NutritionPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [condition, setCondition] = useState("inflammation");
  const [healingFoods, setHealingFoods] = useState<HealingFood[]>([]);
  const [mealPlan, setMealPlan] = useState<MealPlan[]>([]);
  const [activeTab, setActiveTab] = useState<"healing" | "mealplan" | "nexus">("healing");
  const [loading, setLoading] = useState(false);
  const [showAllDays, setShowAllDays] = useState(false);

  const loadHealingFoods = async (cond: string) => {
    setLoading(true);
    try {
      const res = await nutrition.healingFoods(cond);
      setHealingFoods(res.foods);
    } finally {
      setLoading(false);
    }
  };

  const loadMealPlan = async () => {
    setLoading(true);
    try {
      const plan = await nutrition.mealPlan(condition, 7);
      setMealPlan(plan);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab: typeof activeTab) => {
    setActiveTab(tab);
    if (tab === "healing" && healingFoods.length === 0) loadHealingFoods(condition);
    if (tab === "mealplan" && mealPlan.length === 0) loadMealPlan();
  };

  const filteredFoods = searchQuery.trim()
    ? healingFoods.filter((f) =>
        f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.properties.some((p) => p.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : healingFoods;

  const displayedDays = showAllDays ? mealPlan : mealPlan.slice(0, 3);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Leaf className="w-7 h-7 text-emerald-400" /> Nutrition
        </h1>
        <p className="text-white/40 mt-1">Food as medicine — targeted healing through diet.</p>
      </div>

      {/* Condition selector */}
      <div>
        <p className="text-white/40 text-xs uppercase tracking-wider mb-2">Focus Area</p>
        <div className="flex gap-2 flex-wrap">
          {CONDITIONS.map((c) => (
            <button key={c} onClick={() => {
              setCondition(c);
              setHealingFoods([]);
              setMealPlan([]);
              if (activeTab === "healing") loadHealingFoods(c);
            }}
              className={cn("px-4 py-1.5 rounded-full text-sm font-medium transition-all",
                condition === c ? "bg-emerald-600 text-white" : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10")}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/5 rounded-xl p-1">
        {(["healing", "mealplan", "nexus"] as const).map((tab) => (
          <button key={tab} onClick={() => handleTabChange(tab)}
            className={cn("flex-1 py-2 rounded-lg text-sm font-medium transition-all",
              activeTab === tab ? "bg-emerald-600 text-white" : "text-white/40 hover:text-white")}>
            {tab === "healing" ? "Healing Foods" : tab === "mealplan" ? "7-Day Meal Plan" : "Nexus AI"}
          </button>
        ))}
      </div>

      {loading && (
        <div className="grid gap-4">{[1,2,3].map((i) => <div key={i} className="glass rounded-2xl h-28 animate-pulse" />)}</div>
      )}

      {/* Healing Foods */}
      {activeTab === "healing" && !loading && (
        <div className="space-y-4">
          {healingFoods.length > 0 && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search foods or properties…"
                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50" />
            </div>
          )}
          {healingFoods.length === 0 ? (
            <div className="text-center py-12">
              <Button onClick={() => loadHealingFoods(condition)}>Load Healing Foods for {condition}</Button>
            </div>
          ) : filteredFoods.length === 0 ? (
            <p className="text-white/30 text-center py-8">No foods match &quot;{searchQuery}&quot;</p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {filteredFoods.map((food) => (
                <Card key={food.name}>
                  <CardHeader>
                    <CardTitle className="capitalize">{food.name.replace(/-/g, " ")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-white/50 text-xs mb-2">Active compound: <span className="text-white/70">{food.active_compound}</span></p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {food.properties.map((p) => <Badge key={p} variant="emerald">{p}</Badge>)}
                    </div>
                    <p className="text-white/40 text-xs mb-1">Best for</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {food.best_for.map((b) => <Badge key={b} variant="default">{b}</Badge>)}
                    </div>
                    <p className="text-white/60 text-xs leading-relaxed">{food.preparation}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Meal Plan */}
      {activeTab === "mealplan" && !loading && (
        <div className="space-y-3">
          {mealPlan.length === 0 ? (
            <div className="text-center py-12">
              <Button onClick={loadMealPlan}>Generate 7-Day Meal Plan</Button>
            </div>
          ) : (
            <>
              {displayedDays.map((day) => (
                <Card key={day.day}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Day {day.day} — {day.healing_focus}</CardTitle>
                      <Badge variant="emerald">{day.total_calories} kcal</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-3">
                      {day.meals.map((meal) => (
                        <div key={meal.meal} className="flex gap-3">
                          <span className="text-white/40 text-xs w-20 flex-shrink-0 pt-0.5 capitalize">{meal.meal}</span>
                          <div>
                            <p className="text-white/80 text-sm">{meal.foods.join(", ")}</p>
                            {meal.notes && <p className="text-white/40 text-xs">{meal.notes}</p>}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-4 pt-3 border-t border-white/5 text-xs text-white/30">
                      <span>Protein: {day.macros.protein_g}g</span>
                      <span>Carbs: {day.macros.carbs_g}g</span>
                      <span>Fat: {day.macros.fat_g}g</span>
                      <span>Fiber: {day.macros.fiber_g}g</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {mealPlan.length > 3 && (
                <button onClick={() => setShowAllDays((v) => !v)}
                  className="w-full py-2.5 text-white/40 hover:text-white/70 text-sm transition-colors">
                  {showAllDays ? "Show less" : `Show all ${mealPlan.length} days`}
                </button>
              )}
            </>
          )}
        </div>
      )}

      {/* Nexus AI */}
      {activeTab === "nexus" && (
        <NexusInsight
          context="nutrition"
          prompt={`Give me a detailed, personalised nutrition plan for ${condition}. Include specific foods, timing, and what to avoid. Be practical and actionable.`}
          accentClass="bg-emerald-500/15 text-emerald-400"
        />
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import { nutrition, HealingFood, MealPlan, NutritionRec } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Leaf, Search, Sparkles, ChevronRight } from "lucide-react";

const CONDITIONS = ["inflammation", "gut-health", "stress", "detox", "energy", "sleep", "immunity"];

export default function NutritionPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [condition, setCondition] = useState("inflammation");
  const [healingFoods, setHealingFoods] = useState<HealingFood[]>([]);
  const [mealPlan, setMealPlan] = useState<MealPlan[]>([]);
  const [recommendation, setRecommendation] = useState<NutritionRec | null>(null);
  const [activeTab, setActiveTab] = useState<"healing" | "mealplan" | "nexus">("healing");
  const [loading, setLoading] = useState(false);

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

  const loadNexusRec = async () => {
    setLoading(true);
    try {
      const rec = await nutrition.recommendation(condition);
      setRecommendation(rec);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab: typeof activeTab) => {
    setActiveTab(tab);
    if (tab === "healing" && healingFoods.length === 0) loadHealingFoods(condition);
    if (tab === "mealplan" && mealPlan.length === 0) loadMealPlan();
    if (tab === "nexus" && !recommendation) loadNexusRec();
  };

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
            <button
              key={c}
              onClick={() => {
                setCondition(c);
                setHealingFoods([]);
                setMealPlan([]);
                setRecommendation(null);
                if (activeTab === "healing") loadHealingFoods(c);
              }}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                condition === c
                  ? "bg-emerald-600 text-white"
                  : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/5 rounded-xl p-1">
        {(["healing", "mealplan", "nexus"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => handleTabChange(tab)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-emerald-600 text-white"
                : "text-white/40 hover:text-white"
            }`}
          >
            {tab === "healing" ? "Healing Foods" : tab === "mealplan" ? "Meal Plan" : "Nexus AI"}
          </button>
        ))}
      </div>

      {loading && (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="glass rounded-2xl h-28 animate-pulse" />)}
        </div>
      )}

      {/* Healing Foods */}
      {activeTab === "healing" && !loading && (
        <div>
          {healingFoods.length === 0 ? (
            <div className="text-center py-12">
              <Button onClick={() => loadHealingFoods(condition)}>
                Load Healing Foods for {condition}
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {healingFoods.map((food) => (
                <Card key={food.name}>
                  <CardHeader>
                    <CardTitle className="capitalize">{food.name.replace(/-/g, " ")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-white/50 text-xs mb-2">Active: {food.active_compound}</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {food.properties.map((p) => (
                        <Badge key={p} variant="emerald">{p}</Badge>
                      ))}
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
        <div>
          {mealPlan.length === 0 ? (
            <div className="text-center py-12">
              <Button onClick={loadMealPlan}>Generate 7-Day Meal Plan</Button>
            </div>
          ) : (
            <div className="space-y-3">
              {mealPlan.slice(0, 3).map((day) => (
                <Card key={day.day}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Day {day.day}</CardTitle>
                      <Badge variant="emerald">{day.total_calories} kcal</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {day.meals.map((meal) => (
                        <div key={meal.meal} className="flex gap-3">
                          <span className="text-white/40 text-xs w-20 flex-shrink-0 pt-0.5">{meal.meal}</span>
                          <div>
                            <p className="text-white/80 text-sm">{meal.foods.join(", ")}</p>
                            <p className="text-white/40 text-xs">{meal.notes}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-4 mt-3 pt-3 border-t border-white/5 text-xs text-white/30">
                      <span>P: {day.macros.protein_g}g</span>
                      <span>C: {day.macros.carbs_g}g</span>
                      <span>F: {day.macros.fat_g}g</span>
                      <span>Fiber: {day.macros.fiber_g}g</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
              <p className="text-white/30 text-xs text-center">Showing 3 of 7 days</p>
            </div>
          )}
        </div>
      )}

      {/* Nexus AI */}
      {activeTab === "nexus" && !loading && (
        <div>
          {!recommendation ? (
            <div className="text-center py-12">
              <Button onClick={loadNexusRec}>
                <Sparkles className="w-4 h-4 mr-2" />
                Get Nexus Recommendation
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-violet-400" />
                    Nexus AI Insight
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-white/80 leading-relaxed whitespace-pre-line">
                    {recommendation.nexus_insight ?? recommendation.rationale}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Avoid</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {recommendation.avoid.map((a) => (
                      <Badge key={a} variant="rose">{a}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

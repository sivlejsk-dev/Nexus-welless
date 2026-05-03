"use client";

import { useState, useEffect, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { foodMedicine, SymptomAnalysis } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Stethoscope, Plus, X, Search, Sparkles, AlertTriangle,
  CheckCircle2, XCircle, BookOpen, ChevronDown, ChevronUp,
  Leaf, FlaskConical, Library, ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

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
    }}>{content}</ReactMarkdown>
  );
}

const CONDITION_COLORS: Record<string, string> = {
  "Fatigue":              "text-amber-400   bg-amber-400/10   border-amber-400/20",
  "Inflammation":         "text-rose-400    bg-rose-400/10    border-rose-400/20",
  "Anxiety":              "text-violet-400  bg-violet-400/10  border-violet-400/20",
  "Depression":           "text-indigo-400  bg-indigo-400/10  border-indigo-400/20",
  "Poor Sleep":           "text-sky-400     bg-sky-400/10     border-sky-400/20",
  "Gut Issues":           "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
  "Joint Pain":           "text-orange-400  bg-orange-400/10  border-orange-400/20",
  "Brain Fog":            "text-cyan-400    bg-cyan-400/10    border-cyan-400/20",
  "Skin Issues":          "text-pink-400    bg-pink-400/10    border-pink-400/20",
  "Hypertension":         "text-red-400     bg-red-400/10     border-red-400/20",
  "Diabetes Risk":        "text-yellow-400  bg-yellow-400/10  border-yellow-400/20",
  "Thyroid Dysfunction":  "text-teal-400    bg-teal-400/10    border-teal-400/20",
  "High Cholesterol":     "text-orange-300  bg-orange-300/10  border-orange-300/20",
  "Liver Disease":        "text-lime-400    bg-lime-400/10    border-lime-400/20",
  "Kidney Disease":       "text-blue-400    bg-blue-400/10    border-blue-400/20",
  "Cardiovascular Disease": "text-red-500   bg-red-500/10     border-red-500/20",
  "Cancer Prevention":    "text-purple-400  bg-purple-400/10  border-purple-400/20",
  "Immune Dysfunction":   "text-green-400   bg-green-400/10   border-green-400/20",
  "Hormonal Imbalance":   "text-fuchsia-400 bg-fuchsia-400/10 border-fuchsia-400/20",
  "Osteoporosis":         "text-stone-400   bg-stone-400/10   border-stone-400/20",
  "Muscle Weakness":      "text-blue-300    bg-blue-300/10    border-blue-300/20",
  "Migraines":            "text-violet-300  bg-violet-300/10  border-violet-300/20",
  "Allergies":            "text-yellow-300  bg-yellow-300/10  border-yellow-300/20",
  "Obesity":              "text-amber-300   bg-amber-300/10   border-amber-300/20",
  "Anaemia":              "text-rose-300    bg-rose-300/10    border-rose-300/20",
  "Toxic Load":           "text-slate-400   bg-slate-400/10   border-slate-400/20",
  "Fertility Issues":     "text-pink-300    bg-pink-300/10    border-pink-300/20",
  "Menopause Symptoms":   "text-orange-200  bg-orange-200/10  border-orange-200/20",
  "Prostate Health":      "text-blue-400    bg-blue-400/10    border-blue-400/20",
  "Eye Health":           "text-cyan-300    bg-cyan-300/10    border-cyan-300/20",
  "Hair Loss":            "text-amber-200   bg-amber-200/10   border-amber-200/20",
  "Cognitive Decline":    "text-indigo-300  bg-indigo-300/10  border-indigo-300/20",
  "Adhd":                 "text-sky-300     bg-sky-300/10     border-sky-300/20",
  "Fibromyalgia":         "text-violet-200  bg-violet-200/10  border-violet-200/20",
  "Autoimmune Disease":   "text-red-300     bg-red-300/10     border-red-300/20",
  "Gout":                 "text-lime-300    bg-lime-300/10    border-lime-300/20",
};

function colorFor(condition: string) {
  return CONDITION_COLORS[condition] ?? "text-violet-400 bg-violet-400/10 border-violet-400/20";
}

function ConditionCard({ result, defaultExpanded = true }: { result: SymptomAnalysis; defaultExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const cls = colorFor(result.condition);
  const parts = cls.split(" ");
  const textColor = parts[0]; const bgColor = parts[1]; const borderColor = parts[2];

  return (
    <Card className={cn("border", borderColor)}>
      <div role="button" tabIndex={0}
        onClick={() => setExpanded(v => !v)}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && setExpanded(v => !v)}
        className="flex items-center justify-between cursor-pointer select-none p-1">
        <CardTitle className={cn("flex items-center gap-2 text-base", textColor)}>
          <Stethoscope className="w-4 h-4" />{result.condition}
        </CardTitle>
        {expanded ? <ChevronUp className="w-4 h-4 text-white/30" /> : <ChevronDown className="w-4 h-4 text-white/30" />}
      </div>

      {expanded && (
        <div className="space-y-5 mt-4">
          <div>
            <p className="text-white/40 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3 h-3" /> Root Causes &amp; Mechanisms
            </p>
            <ul className="space-y-2">
              {result.root_causes.map((cause, i) => (
                <li key={i} className="flex gap-2.5 text-sm text-white/70">
                  <span className="w-5 h-5 rounded-full bg-white/8 text-white/40 text-xs flex items-center justify-center flex-shrink-0 mt-0.5 font-mono">{i + 1}</span>
                  <span className="leading-relaxed">{cause}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <p className="text-white/40 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3 h-3 text-amber-400" /> Nutrient Deficiencies
              </p>
              <div className="flex flex-wrap gap-1.5">
                {result.deficiencies.map((d) => (
                  <span key={d} className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 border border-amber-500/20 text-amber-300">{d}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-white/40 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <XCircle className="w-3 h-3 text-rose-400" /> Dietary Excesses
              </p>
              <div className="flex flex-wrap gap-1.5">
                {result.excesses.map((e) => (
                  <span key={e} className="px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 border border-rose-500/20 text-rose-300">{e}</span>
                ))}
              </div>
            </div>
          </div>

          <div>
            <p className="text-white/40 text-xs uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Leaf className="w-3 h-3 text-emerald-400" /> Healing Foods (Evidence-Based)
            </p>
            <div className="grid sm:grid-cols-2 gap-2.5">
              {result.healing_foods.map((hf) => (
                <div key={hf.food} className="bg-emerald-500/5 border border-emerald-500/15 rounded-xl p-3 space-y-1">
                  <p className="text-white/90 font-semibold text-sm">{hf.food}</p>
                  <p className="text-white/55 text-xs leading-relaxed">{hf.reason}</p>
                  <p className="text-emerald-400/60 text-[10px] font-mono">{hf.evidence}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-white/40 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <XCircle className="w-3 h-3 text-rose-400" /> Foods to Avoid
            </p>
            <div className="flex flex-wrap gap-1.5">
              {result.avoid.map((a) => (
                <span key={a} className="px-2.5 py-1 rounded-full text-xs bg-rose-500/8 border border-rose-500/15 text-rose-300/80">{a}</span>
              ))}
            </div>
          </div>

          <div className={cn("rounded-xl p-4 border", bgColor, borderColor)}>
            <p className={cn("text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-1.5", textColor)}>
              <CheckCircle2 className="w-3.5 h-3.5" /> Evidence-Based Protocol
            </p>
            <p className="text-white/75 text-sm leading-relaxed">{result.protocol}</p>
          </div>

          {result.nexus_insight && (
            <div className="bg-gradient-to-r from-violet-500/8 to-indigo-500/8 border border-violet-500/15 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <p className="text-violet-300 text-xs font-semibold uppercase tracking-wider">Nexus Personalised Analysis</p>
              </div>
              <NexusMarkdown content={result.nexus_insight} />
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

const COMMON_SYMPTOMS = [
  "fatigue","inflammation","anxiety","depression","poor sleep","gut issues",
  "joint pain","brain fog","skin issues","hypertension","blood sugar","thyroid",
  "cholesterol","migraines","hair loss","immune","hormonal imbalance","gout",
];

function SymptomAnalyser() {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [results, setResults] = useState<SymptomAnalysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [analysed, setAnalysed] = useState(false);

  const addSymptom = (s: string) => {
    const clean = s.trim().toLowerCase();
    if (clean && !symptoms.includes(clean)) setSymptoms(prev => [...prev, clean]);
    setInputValue("");
  };
  const removeSymptom = (s: string) => setSymptoms(prev => prev.filter(x => x !== s));
  const analyse = async () => {
    if (!symptoms.length) return;
    setLoading(true); setResults([]);
    try { const data = await foodMedicine.analyse(symptoms, true); setResults(data); setAnalysed(true); }
    catch { setResults([]); } finally { setLoading(false); }
  };
  const reset = () => { setSymptoms([]); setResults([]); setAnalysed(false); setInputValue(""); };

  if (analysed) return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-white font-bold text-lg">Your Analysis</h2>
          <p className="text-white/40 text-sm">{results.length} condition{results.length !== 1 ? "s" : ""} identified from {symptoms.length} symptom{symptoms.length !== 1 ? "s" : ""}</p>
        </div>
        <Button variant="secondary" size="sm" onClick={reset}><Search className="w-3.5 h-3.5 mr-1.5" />New Analysis</Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {symptoms.map((s) => <span key={s} className="px-3 py-1 rounded-full text-xs bg-white/5 border border-white/10 text-white/50">{s}</span>)}
      </div>
      {results.map((r) => <ConditionCard key={r.condition} result={r} />)}
      {results.length > 0 && (
        <NexusInsight context="food medicine"
          prompt={`I have these symptoms: ${symptoms.join(", ")}. The analysis identified: ${results.map(r => r.condition).join(", ")}. What is the single most important dietary change I should make today, and what does a realistic first week of healing look like?`}
          accentClass="bg-emerald-500/15 text-emerald-400" lazy />
      )}
      {results.length === 0 && (
        <Card><CardContent className="text-center py-8">
          <p className="text-white/40">No conditions matched. Try different symptom descriptions.</p>
          <Button variant="secondary" size="sm" className="mt-4" onClick={reset}>Try Again</Button>
        </CardContent></Card>
      )}
    </div>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Search className="w-4 h-4 text-emerald-400" />What symptoms are you experiencing?</CardTitle>
        <p className="text-white/40 text-sm mt-1">Add as many as apply — the more detail, the better the analysis.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-white/30 text-xs mb-2">Common symptoms — tap to add:</p>
          <div className="flex flex-wrap gap-2">
            {COMMON_SYMPTOMS.map((s) => (
              <button key={s} onClick={() => addSymptom(s)} disabled={symptoms.includes(s)}
                className={cn("px-3 py-1.5 rounded-full text-xs font-medium transition-all border",
                  symptoms.includes(s) ? "bg-emerald-600/20 border-emerald-500/30 text-emerald-300 cursor-default"
                    : "bg-white/5 border-white/10 text-white/50 hover:text-white hover:bg-white/10 hover:border-white/20")}>
                {symptoms.includes(s) && <span className="mr-1">✓</span>}{s}
              </button>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <input type="text" value={inputValue} onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addSymptom(inputValue)}
            placeholder="Type a custom symptom and press Enter…"
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-emerald-500/40 transition-colors" />
          <Button onClick={() => addSymptom(inputValue)} disabled={!inputValue.trim()} size="sm"><Plus className="w-4 h-4" /></Button>
        </div>
        {symptoms.length > 0 && (
          <div>
            <p className="text-white/30 text-xs mb-2">Your symptoms ({symptoms.length}):</p>
            <div className="flex flex-wrap gap-2">
              {symptoms.map((s) => (
                <span key={s} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-emerald-600/20 border border-emerald-500/30 text-emerald-300">
                  {s}<button onClick={() => removeSymptom(s)} className="hover:text-white transition-colors"><X className="w-3 h-3" /></button>
                </span>
              ))}
            </div>
          </div>
        )}
        <Button onClick={analyse} disabled={!symptoms.length || loading} size="lg" className="w-full">
          {loading
            ? <span className="flex items-center gap-2"><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Analysing with Nexus AI…</span>
            : <span className="flex items-center gap-2"><Sparkles className="w-4 h-4" />Analyse My Symptoms</span>}
        </Button>
      </CardContent>
    </Card>
  );
}

interface ConditionMeta { key: string; label: string; }

function ConditionBrowser() {
  const [conditions, setConditions] = useState<ConditionMeta[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<ConditionMeta | null>(null);
  const [detail, setDetail] = useState<SymptomAnalysis | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => { foodMedicine.conditions().then((r) => setConditions(r.conditions)).catch(() => {}); }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) return conditions;
    const q = search.toLowerCase();
    return conditions.filter((c) => c.label.toLowerCase().includes(q));
  }, [conditions, search]);

  const openCondition = async (c: ConditionMeta) => {
    setSelected(c); setDetail(null); setLoadingDetail(true);
    try { const raw = await foodMedicine.condition(c.key); setDetail(raw as unknown as SymptomAnalysis); }
    catch { setDetail(null); } finally { setLoadingDetail(false); }
  };

  if (selected) return (
    <div className="space-y-4">
      <button onClick={() => { setSelected(null); setDetail(null); }}
        className="flex items-center gap-2 text-white/50 hover:text-white text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" /> All Conditions
      </button>
      {loadingDetail && <div className="flex items-center justify-center py-16"><div className="w-6 h-6 border-2 border-white/20 border-t-violet-400 rounded-full animate-spin" /></div>}
      {detail && (
        <>
          <ConditionCard result={detail} defaultExpanded />
          <NexusInsight context="food medicine"
            prompt={`Give me a detailed, personalised 3-paragraph explanation of ${detail.condition}: what causes it nutritionally, the most important foods to eat and why, and a realistic 30-day healing protocol. Be specific and cite mechanisms.`}
            accentClass="bg-emerald-500/15 text-emerald-400" lazy />
        </>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search 36 conditions…"
          className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-violet-500/40 transition-colors" />
      </div>
      <p className="text-white/30 text-xs">{filtered.length} condition{filtered.length !== 1 ? "s" : ""} — click any to see full food medicine protocol</p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {filtered.map((c) => {
          const cls = colorFor(c.label);
          const parts = cls.split(" ");
          const textColor = parts[0]; const bgColor = parts[1]; const borderColor = parts[2];
          return (
            <button key={c.key} onClick={() => openCondition(c)}
              className={cn("text-left p-3.5 rounded-xl border transition-all hover:scale-[1.02] active:scale-[0.98]", bgColor, borderColor, "hover:brightness-125")}>
              <p className={cn("font-semibold text-sm", textColor)}>{c.label}</p>
              <p className="text-white/30 text-xs mt-0.5">Foods, causes &amp; protocol →</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

type Tab = "analyser" | "browser";

export default function FoodMedicinePage() {
  const [tab, setTab] = useState<Tab>("analyser");
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Stethoscope className="w-7 h-7 text-emerald-400" /> Food as Medicine
        </h1>
        <p className="text-white/40 mt-1">Science-backed nutritional analysis across 36 conditions — root causes, healing foods, and evidence-based protocols.</p>
      </div>
      <NexusInsight context="food medicine"
        prompt="In 2-3 sentences explain the concept of food as medicine — how nutritional deficiency causes illness and how targeted food choices can reverse it. Be compelling and cite a specific biochemical mechanism."
        accentClass="bg-emerald-500/15 text-emerald-400" lazy />
      <div className="flex gap-1 p-1 bg-white/4 rounded-xl border border-white/8 w-fit">
        <button onClick={() => setTab("analyser")}
          className={cn("flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
            tab === "analyser" ? "bg-emerald-600/30 text-emerald-300 border border-emerald-500/30" : "text-white/40 hover:text-white/70")}>
          <FlaskConical className="w-3.5 h-3.5" /> Symptom Analyser
        </button>
        <button onClick={() => setTab("browser")}
          className={cn("flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
            tab === "browser" ? "bg-violet-600/30 text-violet-300 border border-violet-500/30" : "text-white/40 hover:text-white/70")}>
          <Library className="w-3.5 h-3.5" /> Condition Library (36)
        </button>
      </div>
      {tab === "analyser" ? <SymptomAnalyser /> : <ConditionBrowser />}
    </div>
  );
}

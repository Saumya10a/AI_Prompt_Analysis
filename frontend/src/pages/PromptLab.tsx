import { useState } from 'react';
import { apiClient } from '../api/client';
import type { PromptInspectionResult } from '../types';
import { ErrorState } from '../components/ErrorState';
import { Send, FileText, Lightbulb, Sparkles, UserCheck, Compass, CheckCircle2 } from 'lucide-react';


const samples = [
  {
    label: 'DSA: Swap Variables',
    prompt: 'write a code to swap variables a and b without a third variable',
  },
  {
    label: 'School Essay',
    prompt: 'write me an essay on my favourite festival',
  },
  {
    label: 'School Science',
    prompt: 'Explain the process of photosynthesis step-by-step in simple words for a 6th grade science project.',
  },
  {
    label: 'Senior Phone Help',
    prompt: 'How do I make the font size bigger and easier to read on my smartphone screen? Explain in plain words.',
  },
  {
    label: 'College Research',
    prompt: 'Summarize the methodology and findings of this research paper on solar energy adoption in under 150 words.',
  },
];

export function PromptLab() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<PromptInspectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    try {
      setLoading(true);
      setError(null);
      setResult(await apiClient.inspectPrompt(prompt));
    } catch (err: any) {
      setError(err.message || 'Failed to inspect prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => { setPrompt(''); setResult(null); setError(null); };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Prompt Lab</h1>
        <p className="text-slate-600 text-sm mt-1">Evaluate prompt clarity, target audience, constraints, and get model recommendations.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-700" />
              Prompt Input
            </h2>
            <span className="text-xs text-slate-500">Quick samples:</span>
          </div>
          
          <div className="mb-4 flex flex-wrap gap-1.5">
            {samples.map(sample => (
              <button 
                key={sample.label} 
                type="button" 
                onClick={() => { setPrompt(sample.prompt); setResult(null); setError(null); }} 
                className="rounded border border-slate-300 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 hover:border-blue-500 hover:bg-blue-50 hover:text-blue-900 transition-colors"
              >
                {sample.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea 
              value={prompt} 
              onChange={e => setPrompt(e.target.value)} 
              placeholder="Enter your prompt here (e.g. 'write a code to swap variables a and b without a third variable')…" 
              className="h-44 w-full resize-y border border-slate-300 p-3 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 rounded" 
              disabled={loading} 
            />
            <div className="flex gap-2">
              <button 
                type="submit" 
                disabled={loading || !prompt.trim()} 
                className="inline-flex items-center gap-2 rounded bg-blue-700 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                <Send className="h-4 w-4" />
                {loading ? 'Analyzing…' : 'Inspect Prompt'}
              </button>
              <button 
                type="button" 
                onClick={handleClear} 
                disabled={loading} 
                className="rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                Clear
              </button>
            </div>
          </form>
        </section>

        <section aria-live="polite" className="border border-slate-200 bg-white p-6 shadow-sm min-h-[360px]">
          {!result && !error && (
            <div className="flex h-full min-h-[300px] flex-col items-center justify-center text-center">
              <Sparkles className="h-8 w-8 text-slate-400" />
              <p className="mt-3 text-sm text-slate-600">Enter a prompt and click <strong>Inspect Prompt</strong> to see the analysis.</p>
            </div>
          )}
          {error && <ErrorState message={error} />}
          {result && (
            <div className="space-y-4">
              {/* Score header */}
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold tabular-nums text-blue-800">{Math.round(result.specificity_score * 100)}</span>
                  <span className="text-xs text-slate-500">/ 100 Score</span>
                </div>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                  result.specificity_score >= 0.75 ? 'bg-emerald-100 text-emerald-800' :
                  result.specificity_score >= 0.50 ? 'bg-blue-100 text-blue-800' :
                  'bg-amber-100 text-amber-800'
                }`}>
                  {result.specificity_score >= 0.75 ? 'High Quality & Specific' :
                   result.specificity_score >= 0.50 ? 'Clear Request' : 'Needs More Detail'}
                </span>
              </div>

              {/* Persona and Intent Badges */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="border border-slate-200 bg-slate-50 p-2 rounded">
                  <div className="flex items-center gap-1.5 text-slate-500 mb-0.5">
                    <UserCheck className="h-3.5 w-3.5 text-blue-700 shrink-0" />
                    <span>Target Persona</span>
                  </div>
                  <span className="font-semibold text-slate-900 block truncate">{result.estimated_age_group || result.detected_audience}</span>
                </div>
                <div className="border border-slate-200 bg-slate-50 p-2 rounded">
                  <div className="flex items-center gap-1.5 text-slate-500 mb-0.5">
                    <Compass className="h-3.5 w-3.5 text-amber-600 shrink-0" />
                    <span>Intent</span>
                  </div>
                  <span className="font-semibold text-slate-900 block truncate">{result.detected_intent}</span>
                </div>
              </div>

              {/* Model Recommendation */}
              {result.model_recommendation && (
                <div className="border border-emerald-300 bg-emerald-50/70 p-3 rounded text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-emerald-900 flex items-center gap-1">
                      <Sparkles className="h-3.5 w-3.5 text-emerald-700" />
                      Recommended Model:
                    </span>
                    <span className="font-mono font-bold bg-emerald-700 text-white px-2 py-0.5 rounded text-[11px]">
                      {result.model_recommendation.recommended_model}
                    </span>
                  </div>
                  <p className="text-slate-700 leading-normal">{result.model_recommendation.reason}</p>
                  {result.model_recommendation.secondary_model && (
                    <p className="text-slate-500 text-[11px] pt-1 border-t border-emerald-200/60">
                      Alternative: <strong>{result.model_recommendation.secondary_model}</strong> · {result.model_recommendation.trade_off}
                    </p>
                  )}
                </div>
              )}

              {/* Score Breakdown */}
              {result.score_breakdown && (
                <div className="grid grid-cols-4 gap-1.5 text-center text-xs">
                  <div className="bg-slate-50 p-1.5 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block">Clarity</span>
                    <span className="font-bold text-blue-800">{Math.round(result.score_breakdown.clarity_score * 100)}/35</span>
                  </div>
                  <div className="bg-slate-50 p-1.5 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block">Context</span>
                    <span className="font-bold text-blue-800">{Math.round(result.score_breakdown.context_score * 100)}/25</span>
                  </div>
                  <div className="bg-slate-50 p-1.5 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block">Guidance</span>
                    <span className="font-bold text-blue-800">{Math.round(result.score_breakdown.constraint_score * 100)}/25</span>
                  </div>
                  <div className="bg-slate-50 p-1.5 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block">Length</span>
                    <span className="font-bold text-blue-800">{Math.round(result.score_breakdown.length_score * 100)}/15</span>
                  </div>
                </div>
              )}

              {/* Metrics */}
              <div className="flex gap-4 text-xs text-slate-600 bg-slate-50 p-2 rounded border border-slate-200">
                <span><strong>Words:</strong> {result.word_count}</span>
                <span><strong>Characters:</strong> {result.character_count}</span>
                <span><strong>Constraints:</strong> {result.constraints_extracted.length}</span>
              </div>

              {/* Constraints */}
              {result.constraints_extracted.length > 0 && (
                <div className="text-xs">
                  <span className="font-semibold text-slate-700 block mb-1">Detected constraints:</span>
                  <div className="flex flex-wrap gap-1">
                    {result.constraints_extracted.map((item, i) => (
                      <span key={i} className="bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded font-mono text-[11px]">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Hints */}
              <div className="text-xs">
                {result.improvement_hints.length > 0 ? (
                  <ul className="space-y-1">
                    {result.improvement_hints.map((hint, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-slate-600">
                        <Lightbulb className="h-3.5 w-3.5 text-amber-500 shrink-0 mt-0.5" />
                        <span>{hint}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="flex items-center gap-1.5 text-emerald-700">
                    <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                    Prompt is well-specified with clear requirements.
                  </p>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

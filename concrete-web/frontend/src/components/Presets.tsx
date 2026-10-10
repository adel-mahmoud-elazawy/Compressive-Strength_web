"use client";

import React from "react";
import { ConcreteMixInput, MixExample } from "@/types";
import { CheckCircle2, FlaskConical } from "lucide-react";

interface PresetsProps {
  examples: MixExample[];
  onSelect: (values: ConcreteMixInput) => void;
  disabled?: boolean;
}

export const Presets: React.FC<PresetsProps> = ({
  examples,
  onSelect,
  disabled = false,
}) => {
  return (
    <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
      <div className="flex items-center gap-2.5 pb-3 mb-4 border-b border-slate-100">
        <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
          <FlaskConical className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
            Pre-Configured Mix Designs
          </h2>
          <p className="text-xs text-slate-400">
            Click any baseline mixture formulation to automatically populate the parameters
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {examples.map((ex, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(ex.values)}
            className="group flex flex-col justify-between text-left p-4 rounded-xl border border-slate-200 hover:border-slate-800 hover:bg-slate-50/60 transition-all text-slate-800 disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-900"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 group-hover:bg-slate-900 group-hover:text-white transition-colors">
                  {ex.tag}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    ex.expected_label === "STRONG"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : "bg-amber-50 text-amber-700 border-amber-200"
                  }`}
                >
                  {ex.expected_label}
                </span>
              </div>

              <h3 className="text-sm font-bold text-slate-900 group-hover:text-slate-950 leading-snug">
                {ex.name}
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed line-clamp-2">
                {ex.description}
              </p>
            </div>

            <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] font-medium text-slate-500 group-hover:text-slate-900">
              <span>Cement: {ex.values.Cement} kg/m³</span>
              <span className="inline-flex items-center gap-1 font-semibold text-slate-900 group-hover:translate-x-0.5 transition-transform">
                Load Mix &rarr;
              </span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
};

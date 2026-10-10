"use client";

import React from "react";
import { Activity, Layers, Database } from "lucide-react";

interface HeaderProps {
  cutoff: number;
  isBackendHealthy: boolean | null;
}

export const Header: React.FC<HeaderProps> = ({ cutoff, isBackendHealthy }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white py-7 px-4 sm:px-6 lg:px-8 shadow-sm">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              Materials & Structural Testing
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700">
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendHealthy === true
                    ? "bg-emerald-400 animate-pulse"
                    : isBackendHealthy === false
                    ? "bg-rose-400"
                    : "bg-amber-400"
                }`}
              />
              {isBackendHealthy === true
                ? "API Connected"
                : isBackendHealthy === false
                ? "API Offline"
                : "Checking API..."}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Concrete Compressive Strength Predictor
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Machine learning platform predicting 28-day cylindrical compressive resistance (MPa)
            and structural grade compliance based on mixture proportions.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="bg-slate-800/90 border border-slate-700/80 rounded-xl px-4 py-2.5 shadow-sm">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-slate-400" />
              Structural Benchmark
            </div>
            <div className="text-base font-bold text-white mt-0.5">
              Cutoff: <span className="text-emerald-400">{cutoff.toFixed(2)} MPa</span>
            </div>
          </div>

          <div className="bg-slate-800/90 border border-slate-700/80 rounded-xl px-4 py-2.5 shadow-sm">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-slate-400" />
              ML Architecture
            </div>
            <div className="text-base font-bold text-slate-200 mt-0.5">
              Gradient Boosting (12 Features)
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

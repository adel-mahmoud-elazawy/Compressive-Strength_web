"use client";

import React from "react";
import { PredictionResponse } from "@/types";
import { CheckCircle2, AlertTriangle, ShieldCheck, HelpCircle, Loader2 } from "lucide-react";

interface ResultCardProps {
  prediction: PredictionResponse | null;
  cutoff: number;
  isLoading: boolean;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  prediction,
  cutoff,
  isLoading,
}) => {
  // 1. Loading State
  if (isLoading) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm text-center flex flex-col items-center justify-center min-h-[420px]">
        <div className="p-3 bg-slate-100 rounded-2xl text-slate-700 mb-4 animate-bounce">
          <Loader2 className="w-8 h-8 animate-spin text-slate-800" />
        </div>
        <h3 className="text-base font-bold text-slate-800">
          Calculating Compressive Resistance...
        </h3>
        <p className="text-xs text-slate-400 mt-1 max-w-xs">
          Computing 12 physical feature interactions and evaluating structural cutoff threshold.
        </p>
      </div>
    );
  }

  // 2. Standby / Empty State
  if (!prediction) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 sm:p-7 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-5 border-b border-slate-100">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Assessment Status
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            <span className="w-2 h-2 rounded-full bg-slate-400" />
            Ready for Evaluation
          </span>
        </div>

        <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-8 text-center my-6">
          <div className="w-12 h-12 bg-white border border-slate-200 rounded-full flex items-center justify-center mx-auto mb-3 text-slate-400 shadow-2xs">
            <ShieldCheck className="w-6 h-6 text-slate-400" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">
            Awaiting Concrete Mix Proportions
          </h3>
          <p className="text-xs text-slate-500 mt-1.5 max-w-xs mx-auto leading-relaxed">
            Configure the mixture parameters on the left or click any preset example below,
            then click <b>Predict Compressive Strength</b>.
          </p>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-600 leading-relaxed">
          <div className="font-bold text-slate-800 mb-1 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            Structural Classification Rule
          </div>
          A concrete mix design is classified as <b className="text-slate-900">STRONG</b> if its
          predicted compressive strength is at or above the dataset median cutoff (
          <b className="text-slate-900">{cutoff.toFixed(2)} MPa</b>). Mixes falling below this
          benchmark are categorized as <b className="text-slate-900">WEAK</b>.
        </div>
      </div>
    );
  }

  // 3. Evaluated Result State
  const isStrong = prediction.is_strong;
  const strength = prediction.predicted_strength_mpa;
  const cutoffVal = prediction.cutoff_mpa;

  // Visual gauge bounds (0 to 85 MPa reference span)
  const barPercent = Math.min(Math.max((strength / 85.0) * 100, 3.0), 100.0);
  const cutoffPercent = Math.min(Math.max((cutoffVal / 85.0) * 100, 0.0), 100.0);

  return (
    <div
      className={`rounded-2xl p-6 sm:p-7 shadow-sm transition-all border ${
        isStrong
          ? "bg-emerald-50/40 border-emerald-300"
          : "bg-amber-50/40 border-amber-300"
      }`}
    >
      {/* Status Bar */}
      <div className="flex items-center justify-between pb-3 mb-5 border-b border-slate-200/60">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
            Assessment Result
          </span>
          <div className="text-xs font-medium text-slate-600 mt-0.5">
            {isStrong
              ? `Meets / exceeds structural benchmark (≥ ${cutoffVal.toFixed(2)} MPa)`
              : `Below structural benchmark (< ${cutoffVal.toFixed(2)} MPa)`}
          </div>
        </div>

        <div
          className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-extrabold tracking-wider border shadow-2xs ${
            isStrong
              ? "bg-emerald-100/90 text-emerald-800 border-emerald-300"
              : "bg-amber-100/90 text-amber-800 border-amber-300"
          }`}
        >
          {isStrong ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
          )}
          {prediction.label} MIX
        </div>
      </div>

      {/* Hero Strength Callout */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 sm:p-6 text-center shadow-xs mb-5">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
          Predicted Compressive Strength
        </div>

        <div className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-none my-2">
          {strength.toFixed(2)}{" "}
          <span className="text-xl sm:text-2xl font-bold text-slate-500">MPa</span>
        </div>

        <div className="text-xs font-semibold text-slate-500 mt-1">
          {prediction.equivalent_psi.toLocaleString()} psi &bull;{" "}
          <span
            className={
              isStrong ? "text-emerald-700 font-bold" : "text-amber-700 font-bold"
            }
          >
            {isStrong ? "Structural Grade Compliance" : "Non-Structural / Lean Mix"}
          </span>
        </div>

        {/* Visual Benchmark Scale */}
        <div className="mt-5 text-left">
          <div className="flex justify-between items-center text-[11px] font-semibold text-slate-500 mb-1.5">
            <span>0 MPa</span>
            <span className="text-rose-600 font-bold">
              Cutoff: {cutoffVal.toFixed(2)} MPa
            </span>
            <span>85 MPa</span>
          </div>

          <div className="relative h-2.5 bg-slate-100 rounded-full overflow-visible border border-slate-200">
            {/* Fill Bar */}
            <div
              style={{ width: `${barPercent}%` }}
              className={`absolute left-0 top-0 bottom-0 rounded-full transition-all duration-500 ${
                isStrong ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            {/* Cutoff Marker */}
            <div
              style={{ left: `${cutoffPercent}%` }}
              title={`Cutoff: ${cutoffVal.toFixed(2)} MPa`}
              className="absolute -top-1 -bottom-1 w-0.5 bg-rose-600 z-10 shadow-xs"
            />
          </div>
        </div>
      </div>

      {/* Calculated Physical Properties Grid */}
      <div className="grid grid-cols-2 gap-2.5 mb-5">
        <div className="bg-white border border-slate-200 rounded-xl p-3 text-center shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Water / Cement (w/c)
          </div>
          <div className="text-lg font-extrabold text-slate-900 mt-0.5">
            {prediction.water_cement_ratio.toFixed(2)}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3 text-center shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Water / Binder (w/b)
          </div>
          <div className="text-lg font-extrabold text-slate-900 mt-0.5">
            {prediction.water_binder_ratio.toFixed(2)}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3 text-center shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Total Binder
          </div>
          <div className="text-lg font-extrabold text-slate-900 mt-0.5">
            {prediction.total_binder_kg_m3.toFixed(1)}{" "}
            <span className="text-xs font-normal text-slate-400">kg/m³</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3 text-center shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Curing Period
          </div>
          <div className="text-lg font-extrabold text-slate-900 mt-0.5">
            {prediction.curing_age_days.toFixed(0)}{" "}
            <span className="text-xs font-normal text-slate-400">Days</span>
          </div>
        </div>
      </div>

      {/* Explanatory Context Box */}
      <div className="bg-white/90 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-600 leading-relaxed shadow-2xs">
        <div className="font-bold text-slate-800 mb-0.5">
          Benchmark Standard:
        </div>
        The <b className="text-slate-900">{prediction.label}</b> classification is determined by
        comparing the predicted compressive strength ({strength.toFixed(2)} MPa) against the
        training dataset median cutoff (<b>{cutoffVal.toFixed(2)} MPa</b>).
      </div>
    </div>
  );
};

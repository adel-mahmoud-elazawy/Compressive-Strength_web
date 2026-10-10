"use client";

import React from "react";
import { ConcreteMixInput, FieldMeta } from "@/types";
import { SliderInput } from "./SliderInput";
import { Layers, Droplets, Mountain, Clock, RotateCcw, ArrowRight, Loader2 } from "lucide-react";

interface MixFormProps {
  fields: FieldMeta[];
  values: ConcreteMixInput;
  onChange: (name: string, val: number) => void;
  onSubmit: () => void;
  onReset: () => void;
  isLoading: boolean;
}

export const MixForm: React.FC<MixFormProps> = ({
  fields,
  values,
  onChange,
  onSubmit,
  onReset,
  isLoading,
}) => {
  // Group fields by category
  const binderFields = fields.filter((f) => f.category === "Binder Materials");
  const waterFields = fields.filter((f) => f.category === "Water & Additives");
  const aggregateFields = fields.filter((f) => f.category === "Aggregates");
  const curingFields = fields.filter((f) => f.category === "Curing Age");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Group 1: Binder Materials */}
      <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2.5 pb-3 mb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              1. Binder Materials (Cementitious)
            </h2>
            <p className="text-xs text-slate-400">
              Primary hydraulic cement and supplementary mineral admixtures
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {binderFields.map((f) => (
            <SliderInput
              key={f.name}
              field={f}
              value={values[f.name]}
              onChange={onChange}
              disabled={isLoading}
            />
          ))}
        </div>
      </section>

      {/* Group 2: Water & Additives */}
      <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2.5 pb-3 mb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
            <Droplets className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              2. Water & Chemical Additives
            </h2>
            <p className="text-xs text-slate-400">
              Workability and water-reduction control
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {waterFields.map((f) => (
            <SliderInput
              key={f.name}
              field={f}
              value={values[f.name]}
              onChange={onChange}
              disabled={isLoading}
            />
          ))}
        </div>
      </section>

      {/* Group 3: Aggregates */}
      <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2.5 pb-3 mb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
            <Mountain className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              3. Aggregates (Granular Skeleton)
            </h2>
            <p className="text-xs text-slate-400">
              Structural gravel and fine matrix sand distribution
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {aggregateFields.map((f) => (
            <SliderInput
              key={f.name}
              field={f}
              value={values[f.name]}
              onChange={onChange}
              disabled={isLoading}
            />
          ))}
        </div>
      </section>

      {/* Group 4: Curing Age */}
      <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2.5 pb-3 mb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              4. Curing Conditions
            </h2>
            <p className="text-xs text-slate-400">
              Moist curing timeframe prior to cylindrical compression test
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {curingFields.map((f) => (
            <SliderInput
              key={f.name}
              field={f}
              value={values[f.name]}
              onChange={onChange}
              disabled={isLoading}
            />
          ))}
        </div>
      </section>

      {/* Action Control Buttons */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-slate-900 hover:bg-slate-800 active:bg-slate-950 text-white font-semibold text-sm rounded-xl shadow-sm hover:shadow transition-all disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Calculating Model Prediction...</span>
            </>
          ) : (
            <>
              <span>Predict Compressive Strength</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onReset}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 px-5 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm rounded-xl border border-slate-300 transition-colors disabled:opacity-50 cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 text-slate-500" />
          <span>Reset Defaults</span>
        </button>
      </div>
    </form>
  );
};

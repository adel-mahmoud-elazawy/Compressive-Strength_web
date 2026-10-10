"use client";

import React, { ChangeEvent } from "react";
import { FieldMeta } from "@/types";

interface SliderInputProps {
  field: FieldMeta;
  value: number;
  onChange: (name: string, val: number) => void;
  disabled?: boolean;
}

export const SliderInput: React.FC<SliderInputProps> = ({
  field,
  value,
  onChange,
  disabled = false,
}) => {
  const handleSliderChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newVal = parseFloat(e.target.value);
    onChange(field.name, isNaN(newVal) ? field.min : newVal);
  };

  const handleNumberChange = (e: ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "") {
      onChange(field.name, field.min);
      return;
    }
    const newVal = parseFloat(raw);
    if (!isNaN(newVal)) {
      // Allow fluid typing but clamp within reasonable bounds
      const clamped = Math.min(Math.max(newVal, field.min), field.max);
      onChange(field.name, clamped);
    }
  };

  // Calculate percentage fill for custom range slider track styling
  const percentage = Math.min(
    Math.max(((value - field.min) / (field.max - field.min)) * 100, 0),
    100
  );

  return (
    <div className="py-2.5">
      <div className="flex items-center justify-between gap-3 mb-1.5">
        <div>
          <label
            htmlFor={`input-${field.name}`}
            className="text-xs sm:text-sm font-semibold text-slate-800 tracking-tight"
          >
            {field.label}
          </label>
          <span className="ml-1.5 text-[11px] font-medium text-slate-400">
            ({field.unit})
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <input
            id={`input-${field.name}`}
            type="number"
            min={field.min}
            max={field.max}
            step={field.step}
            value={value}
            disabled={disabled}
            onChange={handleNumberChange}
            aria-label={`${field.label} in ${field.unit}`}
            className="w-24 px-2.5 py-1 text-right text-sm font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 focus:bg-white transition-colors"
          />
        </div>
      </div>

      {/* Synchronized Range Slider */}
      <div className="relative flex items-center h-5">
        <input
          type="range"
          min={field.min}
          max={field.max}
          step={field.step}
          value={value}
          disabled={disabled}
          onChange={handleSliderChange}
          aria-label={`Slider for ${field.label}`}
          style={{
            background: `linear-gradient(to right, #0f172a 0%, #0f172a ${percentage}%, #e2e8f0 ${percentage}%, #e2e8f0 100%)`,
          }}
          className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-slate-900 disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div className="flex justify-between items-center text-[11px] text-slate-400 mt-1">
        <span>
          Min: {field.min} {field.unit}
        </span>
        <span className="text-slate-400 truncate max-w-[200px]" title={field.description}>
          {field.description}
        </span>
        <span>
          Max: {field.max} {field.unit}
        </span>
      </div>
    </div>
  );
};

"use client";

import React, { useState, useEffect, useCallback } from "react";
import { ConcreteMixInput, PredictionResponse, FieldMeta, MixExample } from "@/types";
import { DEFAULT_MIX, DEFAULT_CUTOFF, FIELD_DEFINITIONS, MIX_PRESETS } from "@/lib/constants";
import { fetchHealth, fetchMetadata, predictStrength, ApiError } from "@/lib/api";
import { Header } from "@/components/Header";
import { MixForm } from "@/components/MixForm";
import { Presets } from "@/components/Presets";
import { ResultCard } from "@/components/ResultCard";
import { StatusAlert } from "@/components/StatusAlert";

export default function Home() {
  const [values, setValues] = useState<ConcreteMixInput>(DEFAULT_MIX);
  const [fields, setFields] = useState<FieldMeta[]>(FIELD_DEFINITIONS);
  const [examples, setExamples] = useState<MixExample[]>(MIX_PRESETS);
  const [cutoff, setCutoff] = useState<number>(DEFAULT_CUTOFF);

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);

  // Check health and load remote metadata on mount
  useEffect(() => {
    let mounted = true;

    async function init() {
      try {
        const health = await fetchHealth();
        if (mounted) {
          setIsBackendHealthy(health.status === "healthy");
          if (health.cutoff_mpa) {
            setCutoff(health.cutoff_mpa);
          }
        }

        const meta = await fetchMetadata();
        if (mounted && meta) {
          if (meta.fields && meta.fields.length > 0) setFields(meta.fields);
          if (meta.examples && meta.examples.length > 0) setExamples(meta.examples);
          if (meta.cutoff_mpa) setCutoff(meta.cutoff_mpa);
        }
      } catch (err) {
        if (mounted) {
          setIsBackendHealthy(false);
          // Metadata and presets fall back to local constants cleanly
        }
      }
    }

    init();
    return () => {
      mounted = false;
    };
  }, []);

  // Update a single mix parameter
  const handleValueChange = (name: string, val: number) => {
    setValues((prev) => ({
      ...prev,
      [name]: val,
    }));
    // Clear previous error on modification
    if (errorMessage) setErrorMessage(null);
  };

  // Run prediction with the current values
  const handlePredict = useCallback(
    async (overrideValues?: ConcreteMixInput) => {
      setIsLoading(true);
      setErrorMessage(null);
      const payload = overrideValues || values;

      try {
        const result = await predictStrength(payload);
        setPrediction(result);
        setCutoff(result.cutoff_mpa);
        setIsBackendHealthy(true);
      } catch (err: unknown) {
        if (err instanceof ApiError) {
          setErrorMessage(err.message);
          if (err.status === 0) setIsBackendHealthy(false);
        } else {
          setErrorMessage("An unexpected error occurred during prediction.");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [values]
  );

  // Load a preset and execute immediate evaluation
  const handleSelectPreset = (presetValues: ConcreteMixInput) => {
    setValues(presetValues);
    handlePredict(presetValues);
  };

  // Reset to standard defaults
  const handleReset = () => {
    setValues(DEFAULT_MIX);
    setPrediction(null);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-900 flex flex-col font-sans antialiased selection:bg-slate-900 selection:text-white">
      {/* Top Header */}
      <Header cutoff={cutoff} isBackendHealthy={isBackendHealthy} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
        {/* Error Alert Banner if an error occurred */}
        {errorMessage && (
          <StatusAlert
            message={errorMessage}
            onRetry={() => handlePredict()}
            type="error"
          />
        )}

        {/* 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (Inputs Form - 7 cols) */}
          <div className="lg:col-span-7">
            <MixForm
              fields={fields}
              values={values}
              onChange={handleValueChange}
              onSubmit={() => handlePredict()}
              onReset={handleReset}
              isLoading={isLoading}
            />
          </div>

          {/* Right Column (Results Display - 5 cols) */}
          <div className="lg:col-span-5 lg:sticky lg:top-8">
            <ResultCard
              prediction={prediction}
              cutoff={cutoff}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Pre-Configured Mix Examples Section */}
        <Presets
          examples={examples}
          onSelect={handleSelectPreset}
          disabled={isLoading}
        />
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Concrete Compressive Strength Assessment Platform &bull; FastAPI + Next.js
          </span>
          <span className="text-slate-400">
            Civil Engineering Machine Learning Pipeline (12 Features)
          </span>
        </div>
      </footer>
    </div>
  );
}

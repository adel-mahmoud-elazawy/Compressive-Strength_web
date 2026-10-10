"use client";

import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface StatusAlertProps {
  message: string;
  onRetry?: () => void;
  type?: "error" | "warning";
}

export const StatusAlert: React.FC<StatusAlertProps> = ({
  message,
  onRetry,
  type = "error",
}) => {
  const isError = type === "error";

  return (
    <div
      className={`rounded-xl p-4 flex items-start gap-3 border shadow-2xs mb-5 ${
        isError
          ? "bg-rose-50 border-rose-200 text-rose-900"
          : "bg-amber-50 border-amber-200 text-amber-900"
      }`}
    >
      <AlertCircle
        className={`w-5 h-5 shrink-0 mt-0.5 ${
          isError ? "text-rose-600" : "text-amber-600"
        }`}
      />
      <div className="flex-1 text-sm">
        <div className="font-bold mb-0.5">
          {isError ? "Operational Error" : "Warning"}
        </div>
        <div className="text-xs leading-relaxed opacity-90">{message}</div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          type="button"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-rose-300 hover:bg-rose-100 text-rose-800 transition-colors shrink-0 shadow-2xs cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};

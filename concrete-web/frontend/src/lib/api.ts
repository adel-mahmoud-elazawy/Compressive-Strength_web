import { ConcreteMixInput, PredictionResponse, MetaResponse, HealthResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number = 500) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });
    if (!res.ok) {
      throw new ApiError(`Health check failed: HTTP ${res.status}`, res.status);
    }
    return await res.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      "Unable to connect to the backend API server. Please ensure the FastAPI backend is running.",
      0
    );
  }
}

export async function fetchMetadata(): Promise<MetaResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/meta`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });
    if (!res.ok) {
      throw new ApiError(`Failed to fetch metadata: HTTP ${res.status}`, res.status);
    }
    return await res.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError("Failed to reach metadata endpoint.", 0);
  }
}

export async function predictStrength(mix: ConcreteMixInput): Promise<PredictionResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mix),
    });

    if (!res.ok) {
      let errorMsg = `Server error (HTTP ${res.status})`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMsg = errorData.detail.map((d: { msg?: string; loc?: string[] }) => `${d.loc?.join(".")}: ${d.msg}`).join(", ");
          } else {
            errorMsg = String(errorData.detail);
          }
        }
      } catch {
        // Fallback to generic message
      }
      throw new ApiError(errorMsg, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      "Failed to communicate with backend server. Check your network or verify if the API is active.",
      0
    );
  }
}

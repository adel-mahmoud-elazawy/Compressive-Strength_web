export interface ConcreteMixInput {
  Cement: number;
  Blast_Furnace_Slag: number;
  Fly_Ash: number;
  Water: number;
  Superplasticizer: number;
  Coarse_Aggregate: number;
  Fine_Aggregate: number;
  Age: number;
}

export interface PredictionResponse {
  predicted_strength_mpa: number;
  label: "STRONG" | "WEAK";
  cutoff_mpa: number;
  is_strong: boolean;
  equivalent_psi: number;
  water_cement_ratio: number;
  water_binder_ratio: number;
  total_binder_kg_m3: number;
  curing_age_days: number;
}

export interface FieldMeta {
  name: keyof ConcreteMixInput;
  label: string;
  unit: string;
  min: number;
  max: number;
  default: number;
  step: number;
  category: "Binder Materials" | "Water & Additives" | "Aggregates" | "Curing Age";
  description: string;
}

export interface MixExample {
  name: string;
  description: string;
  tag: string;
  expected_label: "STRONG" | "WEAK";
  values: ConcreteMixInput;
}

export interface MetaResponse {
  model_name: string;
  cutoff_mpa: number;
  fields: FieldMeta[];
  examples: MixExample[];
}

export interface HealthResponse {
  status: string;
  service: string;
  model_loaded: boolean;
  cutoff_mpa: number;
}

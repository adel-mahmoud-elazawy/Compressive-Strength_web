import { ConcreteMixInput, FieldMeta, MixExample } from "@/types";

export const DEFAULT_MIX: ConcreteMixInput = {
  Cement: 280.0,
  Blast_Furnace_Slag: 0.0,
  Fly_Ash: 0.0,
  Water: 180.0,
  Superplasticizer: 0.0,
  Coarse_Aggregate: 970.0,
  Fine_Aggregate: 780.0,
  Age: 28.0,
};

export const DEFAULT_CUTOFF = 33.72;

export const FIELD_DEFINITIONS: FieldMeta[] = [
  // 1. Binder Materials
  {
    name: "Cement",
    label: "Cement",
    unit: "kg/m³",
    min: 100.0,
    max: 540.0,
    default: 280.0,
    step: 1.0,
    category: "Binder Materials",
    description: "Standard Portland cement content",
  },
  {
    name: "Blast_Furnace_Slag",
    label: "Blast Furnace Slag",
    unit: "kg/m³",
    min: 0.0,
    max: 360.0,
    default: 0.0,
    step: 1.0,
    category: "Binder Materials",
    description: "Granulated blast-furnace slag (SCM)",
  },
  {
    name: "Fly_Ash",
    label: "Fly Ash",
    unit: "kg/m³",
    min: 0.0,
    max: 200.0,
    default: 0.0,
    step: 1.0,
    category: "Binder Materials",
    description: "Pozzolanic mineral admixture from coal combustion",
  },

  // 2. Water & Additives
  {
    name: "Water",
    label: "Water",
    unit: "kg/m³",
    min: 120.0,
    max: 250.0,
    default: 180.0,
    step: 1.0,
    category: "Water & Additives",
    description: "Total batch mixing water",
  },
  {
    name: "Superplasticizer",
    label: "Superplasticizer",
    unit: "kg/m³",
    min: 0.0,
    max: 33.0,
    default: 0.0,
    step: 0.1,
    category: "Water & Additives",
    description: "High-range water-reducing chemical admixture",
  },

  // 3. Aggregates
  {
    name: "Coarse_Aggregate",
    label: "Coarse Aggregate",
    unit: "kg/m³",
    min: 800.0,
    max: 1150.0,
    default: 970.0,
    step: 1.0,
    category: "Aggregates",
    description: "Coarse gravel and crushed rock granular skeleton",
  },
  {
    name: "Fine_Aggregate",
    label: "Fine Aggregate",
    unit: "kg/m³",
    min: 590.0,
    max: 995.0,
    default: 780.0,
    step: 1.0,
    category: "Aggregates",
    description: "Natural sand / fine matrix filler",
  },

  // 4. Curing Age
  {
    name: "Age",
    label: "Curing Age",
    unit: "Days",
    min: 1.0,
    max: 365.0,
    default: 28.0,
    step: 1.0,
    category: "Curing Age",
    description: "Moist curing duration before compression testing",
  },
];

export const MIX_PRESETS: MixExample[] = [
  {
    name: "Standard 28-Day Structural Mix",
    description: "Balanced structural concrete cured for standard 28-day compliance testing.",
    tag: "Standard",
    expected_label: "STRONG",
    values: {
      Cement: 280.0,
      Blast_Furnace_Slag: 100.0,
      Fly_Ash: 0.0,
      Water: 180.0,
      Superplasticizer: 5.0,
      Coarse_Aggregate: 970.0,
      Fine_Aggregate: 770.0,
      Age: 28.0,
    },
  },
  {
    name: "High-Performance Concrete (HPC)",
    description: "Low water-binder ratio with high binder content and superplasticizer for high compressive resistance.",
    tag: "High-Performance",
    expected_label: "STRONG",
    values: {
      Cement: 380.0,
      Blast_Furnace_Slag: 95.0,
      Fly_Ash: 0.0,
      Water: 165.0,
      Superplasticizer: 8.5,
      Coarse_Aggregate: 960.0,
      Fine_Aggregate: 810.0,
      Age: 28.0,
    },
  },
  {
    name: "Fly-Ash Pozzolanic Concrete (56-Day)",
    description: "Sustainable binder mix leveraging fly ash pozzolanic activity over extended 56-day curing.",
    tag: "Pozzolanic",
    expected_label: "STRONG",
    values: {
      Cement: 250.0,
      Blast_Furnace_Slag: 0.0,
      Fly_Ash: 125.0,
      Water: 175.0,
      Superplasticizer: 5.0,
      Coarse_Aggregate: 990.0,
      Fine_Aggregate: 760.0,
      Age: 56.0,
    },
  },
  {
    name: "Lean / Low-Binder Mix (Weak)",
    description: "Lean non-structural mixture tested at 7 days with high water-cement ratio and no mineral admixtures.",
    tag: "Lean / Early",
    expected_label: "WEAK",
    values: {
      Cement: 160.0,
      Blast_Furnace_Slag: 0.0,
      Fly_Ash: 0.0,
      Water: 205.0,
      Superplasticizer: 0.0,
      Coarse_Aggregate: 1050.0,
      Fine_Aggregate: 850.0,
      Age: 7.0,
    },
  },
];

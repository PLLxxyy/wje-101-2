import type { User } from "./user";

export interface BrewStep {
  step_number: number;
  description: string;
  duration_seconds: number;
}

export interface BrewRecipe {
  id: number;
  user_id: number;
  name: string;
  device: string;
  water_temp: number;
  grind_size: string;
  ratio: string;
  steps: BrewStep[];
  created_at: string;
  user: User | null;
}

export interface RecipePayload {
  name: string;
  device: string;
  water_temp: number;
  grind_size: string;
  ratio: string;
  steps: BrewStep[];
}


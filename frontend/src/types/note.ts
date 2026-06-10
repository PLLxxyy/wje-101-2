import type { RoastLevel } from "./enums";
import type { BrewRecipe } from "./recipe";
import type { User } from "./user";

export interface TastingNote {
  id: number;
  user_id: number;
  coffee_name: string;
  origin: string;
  roast_level: RoastLevel;
  flavor_tags: string[];
  aroma_score: number;
  acidity_score: number;
  body_score: number;
  overall_score: number;
  brew_method: string;
  brew_recipe_id: number | null;
  coffee_bean_id: number | null;
  notes_text: string;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  user: User | null;
  brew_recipe: BrewRecipe | null;
  likes_count: number;
  comments_count: number;
  liked_by_me: boolean;
}

export interface NotePayload {
  coffee_name: string;
  origin: string;
  roast_level: RoastLevel;
  flavor_tags: string[];
  aroma_score: number;
  acidity_score: number;
  body_score: number;
  overall_score: number;
  brew_method: string;
  brew_recipe_id: number | null;
  coffee_bean_id: number | null;
  notes_text: string;
  image_url: string | null;
}

export interface Comment {
  id: number;
  note_id: number;
  user_id: number;
  content: string;
  created_at: string;
  user: User | null;
}


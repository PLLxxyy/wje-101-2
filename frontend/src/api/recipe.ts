import request from "@/utils/request";
import type { ApiResponse } from "@/types/api";
import type { BrewRecipe, RecipePayload } from "@/types/recipe";

export interface RecipeListParams {
  device?: string;
  temp_min?: number;
  temp_max?: number;
  search?: string;
  user_id?: string;
}

export async function listRecipes(params: RecipeListParams = {}): Promise<BrewRecipe[]> {
  const response = await request.get<unknown, ApiResponse<BrewRecipe[]>>("/recipes", { params });
  return response.data;
}

export async function getRecipe(recipeId: number): Promise<BrewRecipe> {
  const response = await request.get<unknown, ApiResponse<BrewRecipe>>(`/recipes/${recipeId}`);
  return response.data;
}

export async function createRecipe(payload: RecipePayload): Promise<BrewRecipe> {
  const response = await request.post<unknown, ApiResponse<BrewRecipe>>("/recipes", payload);
  return response.data;
}

export async function updateRecipe(recipeId: number, payload: Partial<RecipePayload>): Promise<BrewRecipe> {
  const response = await request.put<unknown, ApiResponse<BrewRecipe>>(`/recipes/${recipeId}`, payload);
  return response.data;
}

export async function deleteRecipe(recipeId: number): Promise<boolean> {
  const response = await request.delete<unknown, ApiResponse<boolean>>(`/recipes/${recipeId}`);
  return response.data;
}


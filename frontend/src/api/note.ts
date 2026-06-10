import request from "@/utils/request";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type { Comment, NotePayload, TastingNote } from "@/types/note";

export interface NoteListParams {
  page?: number;
  page_size?: number;
  roast_level?: string;
  origin?: string;
  user_id?: number;
  search?: string;
}

export async function listNotes(params: NoteListParams): Promise<PaginatedResponse<TastingNote>> {
  const response = await request.get<unknown, ApiResponse<PaginatedResponse<TastingNote>>>("/notes", { params });
  return response.data;
}

export async function listPopularNotes(limit = 5): Promise<TastingNote[]> {
  const response = await request.get<unknown, ApiResponse<TastingNote[]>>("/notes/popular", { params: { limit } });
  return response.data;
}

export async function getNote(noteId: number): Promise<TastingNote> {
  const response = await request.get<unknown, ApiResponse<TastingNote>>(`/notes/${noteId}`);
  return response.data;
}

export async function createNote(payload: NotePayload): Promise<TastingNote> {
  const response = await request.post<unknown, ApiResponse<TastingNote>>("/notes", payload);
  return response.data;
}

export async function updateNote(noteId: number, payload: Partial<NotePayload>): Promise<TastingNote> {
  const response = await request.put<unknown, ApiResponse<TastingNote>>(`/notes/${noteId}`, payload);
  return response.data;
}

export async function deleteNote(noteId: number): Promise<boolean> {
  const response = await request.delete<unknown, ApiResponse<boolean>>(`/notes/${noteId}`);
  return response.data;
}

export async function likeNote(noteId: number): Promise<{ liked: boolean }> {
  const response = await request.post<unknown, ApiResponse<{ liked: boolean }>>(`/notes/${noteId}/like`);
  return response.data;
}

export async function unlikeNote(noteId: number): Promise<{ liked: boolean }> {
  const response = await request.delete<unknown, ApiResponse<{ liked: boolean }>>(`/notes/${noteId}/like`);
  return response.data;
}

export async function listComments(noteId: number): Promise<Comment[]> {
  const response = await request.get<unknown, ApiResponse<Comment[]>>(`/notes/${noteId}/comments`);
  return response.data;
}

export async function createComment(noteId: number, content: string): Promise<Comment> {
  const response = await request.post<unknown, ApiResponse<Comment>>(`/notes/${noteId}/comments`, { content });
  return response.data;
}

export async function updateComment(commentId: number, content: string): Promise<Comment> {
  const response = await request.put<unknown, ApiResponse<Comment>>(`/comments/${commentId}`, { content });
  return response.data;
}

export async function deleteComment(commentId: number): Promise<boolean> {
  const response = await request.delete<unknown, ApiResponse<boolean>>(`/comments/${commentId}`);
  return response.data;
}


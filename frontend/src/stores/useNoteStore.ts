import { defineStore } from "pinia";
import { ref } from "vue";

import { listNotes, type NoteListParams } from "@/api/note";
import type { TastingNote } from "@/types/note";

export const useNoteStore = defineStore("note", () => {
  const notes = ref<TastingNote[]>([]);
  const currentNote = ref<TastingNote | null>(null);
  const total = ref(0);
  const loading = ref(false);

  async function fetchNotes(params: NoteListParams): Promise<void> {
    loading.value = true;
    try {
      const page = await listNotes(params);
      notes.value = page.items;
      total.value = page.total;
    } finally {
      loading.value = false;
    }
  }

  return { notes, currentNote, total, loading, fetchNotes };
});


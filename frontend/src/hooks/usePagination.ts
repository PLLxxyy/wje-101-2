import { ref } from "vue";

import type { PaginatedResponse } from "@/types/api";

export function usePagination<T>(pageSizeValue = 10) {
  const page = ref(1);
  const pageSize = ref(pageSizeValue);
  const total = ref(0);
  const loading = ref(false);
  const items = ref<T[]>([]);

  async function fetchPage(apiFn: () => Promise<PaginatedResponse<T>>): Promise<void> {
    loading.value = true;
    try {
      const result = await apiFn();
      items.value = result.items;
      total.value = result.total;
      page.value = result.page;
      pageSize.value = result.page_size;
    } finally {
      loading.value = false;
    }
  }

  function goNext(): void {
    if (page.value * pageSize.value < total.value) {
      page.value += 1;
    }
  }

  function goPrev(): void {
    if (page.value > 1) {
      page.value -= 1;
    }
  }

  return { page, pageSize, total, loading, items, fetchPage, goNext, goPrev };
}


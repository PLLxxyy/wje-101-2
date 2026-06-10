import { defineStore } from "pinia";
import { ref } from "vue";

import { listBeans, type BeanListParams } from "@/api/bean";
import type { CoffeeBean } from "@/types/bean";

export const useBeanStore = defineStore("bean", () => {
  const beans = ref<CoffeeBean[]>([]);
  const filters = ref<BeanListParams>({});
  const loading = ref(false);

  async function fetchBeans(params: BeanListParams = {}): Promise<void> {
    loading.value = true;
    filters.value = params;
    try {
      beans.value = await listBeans(params);
    } finally {
      loading.value = false;
    }
  }

  return { beans, filters, loading, fetchBeans };
});


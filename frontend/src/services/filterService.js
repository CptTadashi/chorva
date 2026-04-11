import { reactive } from 'vue';
import api from './api';

export const filterState = reactive({
  selectedCategory: null,
  selectedRegion: null,
  categories: [],
  regions: [],
  
  async fetchCategories() {
    try {
      const response = await api.get('/public/categories');
      this.categories = response.data;
    } catch (error) {
      console.error("Kategoriyalarni yuklashda xato:", error);
    }
  },
  
  async fetchRegions() {
    try {
      const response = await api.get('/public/regions');
      this.regions = response.data;
    } catch (error) {
      console.error("Hududlarni yuklashda xato:", error);
    }
  },
  
  resetFilters() {
    this.selectedCategory = null;
    this.selectedRegion = null;
  }
});

<template>
  <div class="language-switcher">
    <div class="dropdown" @click="toggleDropdown" ref="dropdownRef">
      <div class="selected-lang">
        <span class="lang-icon">{{ currentLocaleIcon }}</span>
        <span class="lang-text">{{ currentLocaleText }}</span>
        <span class="dropdown-arrow">▼</span>
      </div>
      <div class="dropdown-menu" v-if="isOpen">
        <div 
          class="dropdown-item" 
          @click="switchLanguage('zh')"
          :class="{ active: currentLocale === 'zh' }"
        >
          <span class="lang-icon">🇨🇳</span>
          <span class="lang-text">中文</span>
        </div>
        <div 
          class="dropdown-item" 
          @click="switchLanguage('en')"
          :class="{ active: currentLocale === 'en' }"
        >
          <span class="lang-icon">🇺🇸</span>
          <span class="lang-text">English</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement>()

const currentLocale = computed(() => locale.value)

const currentLocaleIcon = computed(() => {
  return currentLocale.value === 'zh' ? '🇨🇳' : '🇺🇸'
})

const currentLocaleText = computed(() => {
  return currentLocale.value === 'zh' ? '中文' : 'English'
})

const switchLanguage = (lang: string) => {
  locale.value = lang
  // 保存语言设置到localStorage
  localStorage.setItem('preferred-language', lang)
  isOpen.value = false
}

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

// 点击外部关闭下拉框
const handleClickOutside = (event: Event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

// 初始化语言设置
onMounted(() => {
  const savedLanguage = localStorage.getItem('preferred-language')
  if (savedLanguage && (savedLanguage === 'zh' || savedLanguage === 'en')) {
    locale.value = savedLanguage
  }
  
  // 添加点击外部关闭下拉框的事件监听
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.dropdown {
  position: relative;
  cursor: pointer;
  user-select: none;
}

.selected-lang {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  min-width: 100px;
}

.selected-lang:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
  margin-left: auto;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(44, 62, 80, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  margin-top: 4px;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  color: white;
  transition: background 0.2s ease;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dropdown-item.active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.lang-icon {
  font-size: 1.1rem;
  line-height: 1;
}

.lang-text {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .selected-lang {
    padding: 6px 10px;
    font-size: 0.8rem;
    min-width: 90px;
  }
  
  .dropdown-item {
    padding: 8px 10px;
  }
  
  .lang-text {
    font-size: 0.8rem;
  }
}
</style> 
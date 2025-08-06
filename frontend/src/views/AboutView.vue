<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ArrowLeftIcon, ChevronUpIcon, ChevronDownIcon, InformationCircleIcon, AcademicCapIcon, CogIcon, ChartBarIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  router.push('/')
}

const features = [
  {
    icon: '🎯',
    title: t('about.features.0.title'),
    description: t('about.features.0.description')
  },
  {
    icon: '📊',
    title: t('about.features.1.title'),
    description: t('about.features.1.description')
  },
  {
    icon: '🔄',
    title: t('about.features.2.title'),
    description: t('about.features.2.description')
  },
  {
    icon: '⚡',
    title: t('about.features.3.title'),
    description: t('about.features.3.description')
  },
  {
    icon: '📈',
    title: t('about.features.4.title'),
    description: t('about.features.4.description')
  },
  {
    icon: '💾',
    title: t('about.features.5.title'),
    description: t('about.features.5.description')
  }
]

const qualityMetrics = [
  { name: t('about.qualityMetrics.0.name'), description: t('about.qualityMetrics.0.description') },
  { name: t('about.qualityMetrics.1.name'), description: t('about.qualityMetrics.1.description') },
  { name: t('about.qualityMetrics.2.name'), description: t('about.qualityMetrics.2.description') },
  { name: t('about.qualityMetrics.3.name'), description: t('about.qualityMetrics.3.description') },
  { name: t('about.qualityMetrics.4.name'), description: t('about.qualityMetrics.4.description') },
  { name: t('about.qualityMetrics.5.name'), description: t('about.qualityMetrics.5.description') },
  { name: t('about.qualityMetrics.6.name'), description: t('about.qualityMetrics.6.description') },
  { name: t('about.qualityMetrics.7.name'), description: t('about.qualityMetrics.7.description') },
  { name: t('about.qualityMetrics.8.name'), description: t('about.qualityMetrics.8.description') }
]

const techStack = computed(() => [
  { 
    category: t('about.techStackCategories.0'), 
    items: ['Vue 3', 'TypeScript', 'Vite', 'Tailwind CSS']
  },
  { 
    category: t('about.techStackCategories.1'), 
    items: ['Python', 'Flask', 'NumPy', 'Pandas']
  },
  { 
    category: t('about.techStackCategories.2'), 
    items: ['A* Path Algorithm', 'BFS Search', 'Graph Theory Analysis']
  },
  { 
    category: t('about.techStackCategories.3'), 
    items: ['Canvas API', 'SVG', 'Chart.js']
  }
])
</script>

<template>
  <div class="min-h-screen bg-[#f0f8ff]">
    <!-- 页头 -->
    <header class="bg-white shadow-sm border-b border-[#6DAEDB]">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center gap-6">
          <button 
            @click="goBack" 
            class="flex items-center gap-2 px-4 py-2 bg-[#f0f8ff] hover:bg-[#e6f3ff] rounded-lg transition-colors duration-200 text-[#173753] font-medium"
          >
            <ArrowLeftIcon class="w-5 h-5" />
            {{ t('about.backButton') }}
          </button>
          <h1 class="text-2xl font-bold text-[#173753]">{{ t('about.title') }}</h1>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto p-6">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- 项目介绍 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <InformationCircleIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.description.title') }}</h2>
          </div>
          <div class="bg-gradient-to-br from-[#f0f8ff] to-[#e6f3ff] rounded-xl p-6 border border-[#6DAEDB]">
            <p class="text-gray-700 leading-relaxed mb-4">
              {{ t('about.intro.description1') }}
            </p>
            <p class="text-gray-700 leading-relaxed">
              {{ t('about.intro.description2') }}
            </p>
          </div>
        </section>

        <!-- 功能特性 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <CogIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.features.title') }}</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="(feature, index) in features" 
              :key="index"
              class="bg-gradient-to-br from-[#f0f8ff] to-[#e6f3ff] rounded-xl p-6 border border-[#6DAEDB] hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              <div class="text-4xl mb-4">{{ feature.icon }}</div>
              <h3 class="text-lg font-semibold text-gray-800 mb-3">{{ feature.title }}</h3>
              <p class="text-gray-600 leading-relaxed">{{ feature.description }}</p>
            </div>
          </div>
        </section>

        <!-- 质量指标 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <ChartBarIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.qualityMetrics.title') }}</h2>
          </div>
          <div class="space-y-4">
            <Disclosure 
              v-for="(metric, index) in qualityMetrics" 
              :key="index"
              as="div" 
              class="bg-white border border-[#6DAEDB] rounded-lg"
            >
              <DisclosureButton class="flex w-full justify-between rounded-lg bg-[#f0f8ff] px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-[#e6f3ff] focus:outline-none focus-visible:ring focus-visible:ring-[#2892D7] focus-visible:ring-opacity-75">
                <span>{{ metric.name }}</span>
                <ChevronUpIcon class="h-5 w-5 text-gray-500 ui-open:rotate-180 ui-open:transform" />
              </DisclosureButton>
              <DisclosurePanel class="px-4 pb-4 pt-2 text-sm text-gray-600">
                {{ metric.description }}
              </DisclosurePanel>
            </Disclosure>
          </div>
        </section>

        <!-- 技术栈 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <AcademicCapIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.techStack.title') }}</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              v-for="(stack, index) in techStack" 
              :key="index"
              class="bg-gradient-to-br from-[#f0f8ff] to-[#e6f3ff] rounded-xl p-6 border border-[#6DAEDB]"
            >
              <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ stack.category }}</h3>
              <ul class="space-y-2">
                <li 
                  v-for="item in stack.items" 
                  :key="item"
                  class="text-gray-600 text-sm flex items-center gap-2"
                >
                  <div class="w-2 h-2 bg-[#2892D7] rounded-full"></div>
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 使用说明 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <InformationCircleIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.usage.title') }}</h2>
          </div>
          <div class="bg-gradient-to-br from-[#f0f8ff] to-[#e6f3ff] rounded-xl p-6 border border-[#6DAEDB]">
            <ol class="space-y-4">
              <li class="flex items-start gap-4">
                <div class="flex-shrink-0 w-8 h-8 bg-[#2892D7] text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                <div>
                  <h4 class="font-semibold text-gray-800 mb-1">{{ t('about.usage.step1.title') }}</h4>
                  <p class="text-gray-600">{{ t('about.usage.step1.description') }}</p>
                </div>
              </li>
              <li class="flex items-start gap-4">
                <div class="flex-shrink-0 w-8 h-8 bg-[#2892D7] text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                <div>
                  <h4 class="font-semibold text-gray-800 mb-1">{{ t('about.usage.step2.title') }}</h4>
                  <p class="text-gray-600">{{ t('about.usage.step2.description') }}</p>
                </div>
              </li>
              <li class="flex items-start gap-4">
                <div class="flex-shrink-0 w-8 h-8 bg-[#2892D7] text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                <div>
                  <h4 class="font-semibold text-gray-800 mb-1">{{ t('about.usage.step3.title') }}</h4>
                  <p class="text-gray-600">{{ t('about.usage.step3.description') }}</p>
                </div>
              </li>
            </ol>
          </div>
        </section>

        <!-- 联系信息 -->
        <section>
          <div class="flex items-center gap-3 mb-6">
            <InformationCircleIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('about.contact.title') }}</h2>
          </div>
          <div class="bg-gradient-to-br from-[#f0f8ff] to-[#e6f3ff] rounded-xl p-6 border border-[#6DAEDB]">
            <p class="text-gray-700 leading-relaxed">
              {{ t('about.contact.description') }}
            </p>
          </div>
        </section>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="mt-12 pt-8 border-t border-[#6DAEDB]">
      <p class="text-center text-gray-500 text-sm">&copy; 2024 {{ t('app.title') }}</p>
    </div>
  </div>
</template>

<style scoped>
/* 响应式设计 */
@media (max-width: 768px) {
  .max-w-7xl {
    @apply px-4;
  }
  
  .p-6 {
    @apply p-4;
  }
  
  .p-8 {
    @apply p-4;
  }
  
  .text-2xl {
    @apply text-xl;
  }
  
  .gap-6 {
    @apply gap-4;
  }
  
  .grid {
    @apply grid-cols-1;
  }
}
</style> 
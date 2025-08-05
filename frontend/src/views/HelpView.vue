<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ArrowLeftIcon, ChevronUpIcon, QuestionMarkCircleIcon, InformationCircleIcon, DocumentTextIcon, CogIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  router.push('/')
}

const helpSections = computed(() => [
  {
    title: t('help.fileUpload.title'),
    icon: '📁',
    content: [
      t('help.fileUpload.content.0'),
      t('help.fileUpload.content.1'),
      t('help.fileUpload.content.2'),
      t('help.fileUpload.content.3'),
      t('help.fileUpload.content.4')
    ]
  },
  {
    title: t('help.analysis.title'),
    icon: '📊',
    content: [
      t('help.analysis.content.0'),
      t('help.analysis.content.1'),
      t('help.analysis.content.2'),
      t('help.analysis.content.3'),
      t('help.analysis.content.4')
    ]
  },
  {
    title: t('help.results.title'),
    icon: '📈',
    content: [
      t('help.results.content.0'),
      t('help.results.content.1'),
      t('help.results.content.2'),
      t('help.results.content.3'),
      t('help.results.content.4')
    ]
  },
  {
    title: t('help.export.title'),
    icon: '💾',
    content: [
      t('help.export.content.0'),
      t('help.export.content.1'),
      t('help.export.content.2'),
      t('help.export.content.3'),
      t('help.export.content.4')
    ]
  }
])

const faqs = [
  {
    question: t('help.faqs.0.question'),
    answer: t('help.faqs.0.answer')
  },
  {
    question: t('help.faqs.1.question'),
    answer: t('help.faqs.1.answer')
  },
  {
    question: t('help.faqs.2.question'),
    answer: t('help.faqs.2.answer')
  },
  {
    question: t('help.faqs.3.question'),
    answer: t('help.faqs.3.answer')
  },
  {
    question: t('help.faqs.4.question'),
    answer: t('help.faqs.4.answer')
  },
  {
    question: t('help.faqs.5.question'),
    answer: t('help.faqs.5.answer')
  }
]

const quickSteps = computed(() => [
  {
    step: 1,
    title: t('help.quickSteps.0.title'),
    description: t('help.quickSteps.0.description'),
    icon: '📁'
  },
  {
    step: 2,
    title: t('help.quickSteps.1.title'),
    description: t('help.quickSteps.1.description'),
    icon: '⚡'
  },
  {
    step: 3,
    title: t('help.quickSteps.2.title'),
    description: t('help.quickSteps.2.description'),
    icon: '📊'
  },
  {
    step: 4,
    title: t('help.quickSteps.3.title'),
    description: t('help.quickSteps.3.description'),
    icon: '💾'
  }
])

const troubleshooting = [
  {
    problem: '文件上传失败',
    solution: '检查文件格式是否为JSON，文件大小是否超过限制。确保文件没有损坏。'
  },
  {
    problem: '分析过程中断',
    solution: '刷新页面重新上传文件。如果问题持续，请检查网络连接。'
  },
  {
    problem: '结果不准确',
    solution: '确保地下城数据完整，包含房间和走廊信息。检查文件格式是否正确。'
  },
  {
    problem: '页面加载缓慢',
    solution: '清除浏览器缓存，关闭其他占用资源的程序。'
  }
]
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页头 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center gap-6">
          <button 
            @click="goBack" 
            class="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 text-gray-700 font-medium"
          >
            <ArrowLeftIcon class="w-5 h-5" />
            {{ t('help.backButton') }}
          </button>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-800">{{ t('help.title') }}</h1>
            <p class="text-gray-600 text-sm">{{ t('help.subtitle') }}</p>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto p-6">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- 快速开始 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <InformationCircleIcon class="w-8 h-8 text-blue-600" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('help.quickStart.title') }}</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              v-for="step in quickSteps" 
              :key="step.step"
              class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center text-lg font-bold">
                  {{ step.step }}
                </div>
                <div class="text-2xl">{{ step.icon }}</div>
              </div>
              <h3 class="text-lg font-semibold text-gray-800 mb-3">{{ step.title }}</h3>
              <p class="text-gray-600 leading-relaxed">{{ step.description }}</p>
            </div>
          </div>
        </section>

        <!-- 详细说明 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-green-600" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('help.detailedGuide.title') }}</h2>
          </div>
          <div class="space-y-4">
            <Disclosure 
              v-for="(section, index) in helpSections" 
              :key="index"
              as="div" 
              class="bg-white border border-gray-200 rounded-lg"
            >
              <DisclosureButton class="flex w-full justify-between rounded-lg bg-gray-50 px-6 py-4 text-left text-lg font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-green-500 focus-visible:ring-opacity-75">
                <div class="flex items-center gap-3">
                  <span class="text-2xl">{{ section.icon }}</span>
                  <span>{{ section.title }}</span>
                </div>
                <ChevronUpIcon class="h-6 w-6 text-gray-500 ui-open:rotate-180 ui-open:transform" />
              </DisclosureButton>
              <DisclosurePanel class="px-6 pb-6 pt-4">
                <ul class="space-y-3">
                  <li 
                    v-for="(item, itemIndex) in section.content" 
                    :key="itemIndex"
                    class="flex items-start gap-3 text-gray-600"
                  >
                    <div class="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </DisclosurePanel>
            </Disclosure>
          </div>
        </section>

        <!-- 常见问题 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <QuestionMarkCircleIcon class="w-8 h-8 text-purple-600" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('help.faq.title') }}</h2>
          </div>
          <div class="space-y-4">
            <Disclosure 
              v-for="(faq, index) in faqs" 
              :key="index"
              as="div" 
              class="bg-white border border-gray-200 rounded-lg"
            >
              <DisclosureButton class="flex w-full justify-between rounded-lg bg-gray-50 px-6 py-4 text-left text-lg font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-purple-500 focus-visible:ring-opacity-75">
                <span>{{ faq.question }}</span>
                <ChevronUpIcon class="h-6 w-6 text-gray-500 ui-open:rotate-180 ui-open:transform" />
              </DisclosureButton>
              <DisclosurePanel class="px-6 pb-6 pt-4 text-gray-600 leading-relaxed">
                {{ faq.answer }}
              </DisclosurePanel>
            </Disclosure>
          </div>
        </section>

        <!-- 故障排除 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <CogIcon class="w-8 h-8 text-orange-600" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('help.troubleshooting.title') }}</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div 
              v-for="(item, index) in troubleshooting" 
              :key="index"
              class="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-6 border border-orange-200"
            >
              <h3 class="text-lg font-semibold text-gray-800 mb-3">{{ item.problem }}</h3>
              <p class="text-gray-600 leading-relaxed">{{ item.solution }}</p>
            </div>
          </div>
        </section>

        <!-- 联系支持 -->
        <section>
          <div class="flex items-center gap-3 mb-6">
            <InformationCircleIcon class="w-8 h-8 text-teal-600" />
            <h2 class="text-2xl font-bold text-gray-800">{{ t('help.support.title') }}</h2>
          </div>
          <div class="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-xl p-6 border border-teal-200">
            <p class="text-gray-700 leading-relaxed mb-4">
              {{ t('help.support.description') }}
            </p>
            <div class="flex gap-4">
              <button 
                @click="router.push('/')"
                class="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors duration-200"
              >
                {{ t('help.support.startAnalysis') }}
              </button>
              <button 
                @click="router.push('/about')"
                class="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors duration-200"
              >
                {{ t('help.support.learnMore') }}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-12">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <p class="text-center text-gray-500 text-sm">&copy; 2024 地下城适配器</p>
      </div>
    </footer>
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
  
  .flex {
    @apply flex-col;
  }
}
</style> 
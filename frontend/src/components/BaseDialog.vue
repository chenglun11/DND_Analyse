<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel
              :class="[
                'relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all',
                sizeClasses
              ]"
            >
              <!-- Header -->
              <div v-if="title || $slots.header" class="px-6 pt-6 pb-4">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <div
                      v-if="icon"
                      :class="[
                        'flex h-10 w-10 items-center justify-center rounded-full',
                        iconColorClasses
                      ]"
                    >
                      <component :is="icon" class="h-6 w-6" />
                    </div>
                    <div :class="icon ? 'ml-4' : ''">
                      <DialogTitle
                        v-if="title"
                        as="h3"
                        class="text-lg font-semibold leading-6 text-gray-900"
                      >
                        {{ title }}
                      </DialogTitle>
                      <slot name="header" />
                    </div>
                  </div>
                  <button
                    v-if="closable"
                    @click="handleClose"
                    class="rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <span class="sr-only">{{t('common.close')}}</span>
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>
                <div v-if="description" class="mt-2">
                  <p class="text-sm text-gray-500">{{ description }}</p>
                </div>
              </div>

              <!-- Content -->
              <div class="px-6" :class="{ 'pt-6': !title && !$slots.header }">
                <slot />
              </div>

              <!-- Footer -->
              <div
                v-if="$slots.footer || showDefaultActions"
                class="px-6 py-4 bg-gray-50 flex flex-col sm:flex-row gap-3 sm:justify-end"
              >
                <slot name="footer">
                  <template v-if="showDefaultActions">
                    <button
                      v-if="showCancel"
                      @click="handleCancel"
                      type="button"
                      class="w-full sm:w-auto inline-flex justify-center rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-colors"
                    >
                      {{ cancelText }}
                    </button>
                    <button
                      v-if="showConfirm"
                      @click="handleConfirm"
                      type="button"
                      :disabled="confirmDisabled"
                      :class="[
                        'w-full sm:w-auto inline-flex justify-center rounded-md px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors',
                        confirmDisabled
                          ? 'bg-gray-300 cursor-not-allowed'
                          : confirmTypeClasses
                      ]"
                    >
                      {{ confirmText }}
                    </button>
                  </template>
                </slot>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

type DialogSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
type DialogType = 'info' | 'success' | 'warning' | 'error'
type ConfirmType = 'primary' | 'danger' | 'success' | 'warning'

interface Props {
  open: boolean
  title?: string
  description?: string
  size?: DialogSize
  type?: DialogType
  icon?: any
  closable?: boolean
  showDefaultActions?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  cancelText?: string
  confirmText?: string
  confirmType?: ConfirmType
  confirmDisabled?: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'cancel'): void
  (e: 'confirm'): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  type: 'info',
  closable: true,
  showDefaultActions: false,
  showCancel: true,
  showConfirm: true,
  cancelText: '取消',
  confirmText: '确定',
  confirmType: 'primary',
  confirmDisabled: false
})

const emit = defineEmits<Emits>()

// Size classes
const sizeClasses = computed(() => {
  const sizeMap = {
    sm: 'sm:max-w-sm sm:w-full sm:mx-4',
    md: 'sm:max-w-md sm:w-full sm:mx-4',
    lg: 'sm:max-w-lg sm:w-full sm:mx-4',
    xl: 'sm:max-w-xl sm:w-full sm:mx-4',
    '2xl': 'sm:max-w-2xl sm:w-full sm:mx-4',
    full: 'sm:max-w-full sm:w-full sm:mx-4'
  }
  return sizeMap[props.size]
})

// Icon color classes based on type
const iconColorClasses = computed(() => {
  const colorMap = {
    info: 'bg-blue-100 text-blue-600',
    success: 'bg-green-100 text-green-600',
    warning: 'bg-yellow-100 text-yellow-600',
    error: 'bg-red-100 text-red-600'
  }
  return colorMap[props.type]
})

// Confirm button type classes
const confirmTypeClasses = computed(() => {
  const typeMap = {
    primary: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    danger: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 focus:ring-green-500',
    warning: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
  }
  return typeMap[props.confirmType]
})

const handleClose = () => {
  emit('close')
}

const handleCancel = () => {
  emit('cancel')
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
}
</script>

<style scoped>
/* Additional animations for smooth transitions */
.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.3s ease;
}

.dialog-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.dialog-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

/* Focus styles */
button:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* Backdrop blur for better visual separation */
.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}
</style>
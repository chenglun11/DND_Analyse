<template>
  <component
    :is="tag"
    :type="tag === 'button' ? type : undefined"
    :href="tag === 'a' ? href : undefined"
    :to="tag === 'router-link' ? to : undefined"
    :disabled="disabled"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    
    <span :class="{ 'opacity-0': loading }" class="flex items-center gap-2">
      <component v-if="iconLeft" :is="iconLeft" :class="iconClasses" />
      <slot />
      <component v-if="iconRight" :is="iconRight" :class="iconClasses" />
    </span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'ghost' | 'outline'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
type ButtonTag = 'button' | 'a' | 'router-link'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  tag?: ButtonTag
  type?: 'button' | 'submit' | 'reset'
  href?: string
  to?: string | object
  disabled?: boolean
  loading?: boolean
  block?: boolean
  rounded?: boolean
  iconLeft?: any
  iconRight?: any
}

interface Emits {
  (e: 'click', event: Event): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  tag: 'button',
  type: 'button',
  disabled: false,
  loading: false,
  block: false,
  rounded: false
})

const emit = defineEmits<Emits>()

// Base classes
const baseClasses = 'relative inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

// Variant classes
const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-[#2892D7] text-white hover:bg-[#1D70A2] focus:ring-[#2892D7] active:bg-[#173753]',
    secondary: 'bg-[#1D70A2] text-white hover:bg-[#173753] focus:ring-[#1D70A2] active:bg-[#1B4353]',
    success: 'bg-[#2892D7] text-white hover:bg-[#1D70A2] focus:ring-[#2892D7] active:bg-[#173753]',
    danger: 'bg-[#173753] text-white hover:bg-[#1B4353] focus:ring-[#173753] active:bg-[#0f2a3a]',
    warning: 'bg-[#1D70A2] text-white hover:bg-[#173753] focus:ring-[#1D70A2] active:bg-[#1B4353]',
    info: 'bg-[#6DAEDB] text-white hover:bg-[#2892D7] focus:ring-[#6DAEDB] active:bg-[#1D70A2]',
    ghost: 'text-[#173753] hover:bg-[#f0f8ff] focus:ring-[#2892D7] active:bg-[#e6f3ff]',
    outline: 'border border-[#6DAEDB] text-[#173753] bg-white hover:bg-[#f0f8ff] focus:ring-[#2892D7] active:bg-[#e6f3ff]'
  }
  return variants[props.variant]
})

// Size classes
const sizeClasses = computed(() => {
  const sizes = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg'
  }
  return sizes[props.size]
})

// Border radius classes
const radiusClasses = computed(() => {
  if (props.rounded) {
    return 'rounded-full'
  }
  const radiusSizes = {
    xs: 'rounded',
    sm: 'rounded-md',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-lg'
  }
  return radiusSizes[props.size]
})

// Block classes
const blockClasses = computed(() => {
  return props.block ? 'w-full' : ''
})

// Icon classes
const iconClasses = computed(() => {
  const iconSizes = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
    xl: 'h-6 w-6'
  }
  return iconSizes[props.size]
})

// Combined classes
const buttonClasses = computed(() => {
  return [
    baseClasses,
    variantClasses.value,
    sizeClasses.value,
    radiusClasses.value,
    blockClasses.value
  ].join(' ')
})

const handleClick = (event: Event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* Loading animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Focus ring styling */
button:focus,
a:focus {
  outline: none;
}

/* Hover effects */
button:not(:disabled):hover,
a:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

button:not(:disabled):active,
a:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* Disabled state */
button:disabled {
  transform: none !important;
  box-shadow: none !important;
}
</style>
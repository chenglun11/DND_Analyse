<template>
  <svg 
    :class="classes" 
    :width="size" 
    :height="size" 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: string | number
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  class: ''
})

const classes = computed(() => {
  return `text-current ${props.class}`
})
</script> 
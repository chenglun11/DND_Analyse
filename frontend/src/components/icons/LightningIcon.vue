<template>
  <svg 
    :class="classes" 
    :width="size" 
    :height="size" 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
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
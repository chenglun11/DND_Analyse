<template>
  <svg 
    :class="classes" 
    :width="size" 
    :height="size" 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
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
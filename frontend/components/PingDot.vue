<template>
  <div class="flex flex-col justify-center h-auto">
    <figure class="absolute w-4 h-4 rounded-full" :class="{'bg-green-600': up, 'bg-red-600': !up, 'animate-pulse': !up}"/>
    <figure class="w-4 h-4 rounded-full" :class="{'bg-green-600': up, 'bg-red-600': !up, 'animate-ping': up, 'invisible': !up}" />
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  props: {
    up: Boolean,
  },
})
</script>
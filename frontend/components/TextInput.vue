
<template>
  <section>
    <label :for="name">{{ description }}</label>
    <input
      :id="name"
      :name="name"
      class="bg-gray-800 rounded-md w-full p-1"
      :placeholder="placeholder"
      :value="value"
      @input="$emit('input', $event.target.value)"
    />
  </section>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: ['value', 'placeholder', 'name', 'description'],
})
</script>

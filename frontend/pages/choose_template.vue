<template>
  <div class="space-y-2">
    <div v-if="$apollo.loading" class="flex flex-row justify-center">
      <Loader />
    </div>
    <section v-else>
      <div class="flex flex-col md:flex-row w-full justify-center flex-wrap">
        <NuxtLink
          v-for="template in allTemplates"
          :key="template.name"
          :to="'/add/' + template.name"
          class="
            bg-gray-800
            rounded-md
            text-center
            transition
            duaration-150
            hover:transform
            hover:scale-105
            m-2
            w-full
            md:w-72
            drop-shadow-xl
          "
        >
          <button>
            <div class="h-full">
              <figure class="w-full h-1.5 bg-green-600 rounded-t-md" />
            </div>
            <div class="p-8">
              <h2 class="text-xl pb-2">{{template.title}}</h2>
              <p>{{template.description}}</p>
            </div>
          </button>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import allTemplates from '~/apollo/queries/allTemplates.gql'

export default Vue.extend({
  apollo: {
    allTemplates: {
      prefetch: true,
      query: allTemplates,
    },
  },
})
</script>

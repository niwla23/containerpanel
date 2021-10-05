<template>
  <section>
    <nuxt-link :to="'/server/' + server_id">
      <button
        class="
          bg-gray-800
          rounded-md
          lg:h-20
          w-full
          p-4
          text-white text-left
          overflow-scroll
        "
      >
        <div class="flex flex-row flex-nowrap lg:flex-nowrap">
          <div class="flex-col justify-center mr-6 ml-2 hidden sm:flex">
            <ping-dot :up="up" />
          </div>
          <section class="lg:flex lg:flex-row lg:w-full">
            <div class="flex-grow">
              <h2 class="font-bold flex flex-row space-x-2">
                <p>{{ name }}</p>
                <ping-dot :up="up" class="block sm:hidden" />
              </h2>
              <small
                >{{ up ? 'Up' : 'Down' }} for
                {{ (status_time / 60 / 60).toFixed(2) }} hours</small
              >
            </div>
            <div class="flex flex-row space-x-2">
              <figure>
                <p class="text-gray-200">
                  <fa icon="microchip" class="mr-2" />
                  {{ cpu.toFixed(2) }}%
                </p>
                <p class="text-gray-200">
                  <fa icon="memory" class="mr-2" />
                  {{ memory }}
                </p>
              </figure>
              <figure>
                <p class="text-gray-200">
                  <fa icon="ethernet" class="mr-2" />
                  {{ port }}
                </p>
                <p class="text-gray-200">
                  <fa icon="save" class="mr-2" />
                  {{ sftpPort }}
                </p>
              </figure>
            </div>
          </section>
        </div>
      </button>
    </nuxt-link>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  props: {
    name: String,
    status_time: Number,
    up: Boolean,
    cpu: Number,
    memory: String,
    port: Number,
    sftpPort: Number,
    server_id: String,
  },
})
</script>
<template>
  <section>
    <div v-if="$apollo.loading" class="flex flex-row justify-center">
      <Loader />
    </div>
    <div v-else>
      <h1 class="text-xl">{{ server.description }}</h1>
      <div
        class="
          md:flex md:flex-row
          md:w-full
          md:space-x-4
          space-y-4
          md:space-y-0
        "
      >
        <div class="space-y-4 flex flex-col">
          <div class="bg-gray-800 p-4 rounded-md w-full md:w-64 flex-grow">
            <h2 class="text-lg">Control</h2>

            <p class="text-green-400 pb-1 flex flex-row">
              <span v-if="updatingState">
                <fa class="animate-spin mr-2" icon="cog" />
              </span>
              <ping-dot v-else class="mr-2" :up="server.state.running" />
              {{ server.state.running ? 'Running' : 'Down' }}
            </p>

            <div v-if="server.state.running" class="flex flex-row space-x-1">
              <button
                class="
                  bg-red-700
                  p-1
                  rounded-md
                  text-sm
                  pr-2
                  pl-2
                  cursor-pointer
                "
                type="submit"
                @click="updateState('stop')"
              >
                Stop
              </button>
              <button
                class="
                  bg-red-700
                  p-1
                  rounded-md
                  text-sm
                  pr-2
                  pl-2
                  cursor-pointer
                "
                type="submit"
                @click="updateState('restart')"
              >
                Restart
              </button>
              <button
                class="
                  bg-red-700
                  p-1
                  rounded-md
                  text-sm
                  pr-2
                  pl-2
                  cursor-pointer
                "
                type="submit"
                @click="updateState('kill')"
              >
                Kill
              </button>
            </div>
            <div v-else class="flex flex-row space-x-1">
              <button
                class="
                  bg-green-700
                  p-1
                  rounded-md
                  text-sm
                  pr-2
                  pl-2
                  cursor-pointer
                "
                type="submit"
                @click="updateState('start')"
              >
                Start
              </button>
            </div>
            <h2 class="text-lg pt-4">Info</h2>
            <div class="text-gray-400">
              <table>
                <tbody>
                  <tr>
                    <td>
                      <fa icon="ethernet" class="mr-1" />
                    </td>
                    <td class="pl-1">{{ server.port }}</td>
                  </tr>
                  <tr>
                    <td>
                      <fa icon="save" class="mr-1" />
                    </td>
                    <td class="pl-1">{{ server.sftpPort }}</td>
                  </tr>
                  <tr>
                    <td>
                      <fa icon="microchip" class="mr-1" />
                    </td>
                    <td class="pl-1">
                      {{ server.state.cpuUsage.toFixed(2) }}%
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <fa icon="memory" class="mr-1" />
                    </td>
                    <td class="pl-1">
                      {{ bytesToString(server.state.memoryUsage) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="bg-gray-800 p-4 rounded-md flex-grow">
            <h2 class="text-lg">User Access</h2>
            <ul class="text-gray-400 list-disc pl-4">
              <li v-for="user in server.allowed_users" :key="user">
                {{ user }}
              </li>
            </ul>
          </div>
        </div>

        <div class="flex-grow space-y-4">
          <div class="bg-gray-800 p-4 rounded-md">
            <h2 class="text-lg">Console</h2>
            <div
              class="
                bg-gray-900
                p-2
                rounded-md
                logs-container
                h-96
                flex flex-col
              "
              id="logs-container"
            >
              <code
                class="text-xs text-gray-300 flex-grow overflow-y-scroll"
                id="logs"
                ref="logs"
              >
                <br />
                <transition-group name="logs" tag="ul">
                  <li v-for="line in server.logs" :key="line">
                    {{ line.split(' ').slice(1).join(' ') }}
                  </li>
                </transition-group>
              </code>
              <div class="flex flex-row pt-2">
                <span class="text-yellow-500 pr-1 text-bold"
                  ><fa icon="chevron-right"
                /></span>
                <input
                  placeholder="Type a command..."
                  class="w-full text-gray-100 bg-gray-900"
                  v-model="command"
                  @keyup.enter="executeCommand"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
import PingDot from '~/components/PingDot.vue'
import serverQuery from '~/apollo/queries/server.gql'
import serverStateMutation from '~/apollo/mutations/serverState.gql'
import execCommandMutation from '~/apollo/mutations/execCommand.gql'
import { bytesToString } from '~/helpers'

export default Vue.extend({
  components: { PingDot },
  data: () => {
    return {
      serverStateMutation: serverStateMutation,
      updatingState: false,
      command: '',
    }
  },
  methods: {
    bytesToString: bytesToString,
    updateState: function (action: 'start' | 'stop' | 'restart' | 'kill') {
      this.updatingState = true
      console.log(this.$route)
      this.$apollo
        .mutate({
          mutation: serverStateMutation,
          variables: { serverId: this.serverId, action: action },
        })
        .then(() => {
          if (action === 'restart') {
            this.updatingState = false
          }
        })
    },
    executeCommand: function () {
      this.$apollo.mutate({
        mutation: execCommandMutation,
        variables: { serverId: this.serverId, command: this.command },
      })
      this.command = ''
    },
  },
  watch: {
    server: function (newServer, oldServer) {
      if (oldServer) {
        if (newServer.state.running != oldServer.state.running) {
          this.updatingState = false
        }
        if (newServer.logs != oldServer.logs) {
          setTimeout(() => {
            if (this.$refs.logs) {
              let scrollHeight = this.$refs.logs.scrollHeight
              this.$refs.logs.scrollTop = scrollHeight
              this.$refs.logs.scrollBy(0, 100)
            }
          }, 50)
        }
      }
    },
  },
  computed: {
    serverId: function () {
      return this.$route.params.id
    },
  },

  apollo: {
    server: {
      prefetch: true,
      query: serverQuery,
      variables() {
        return {
          serverId: this.serverId,
        }
      },
      pollInterval: 1000,
    },
  },
})
</script>


<style scoped>
.logs-enter-active,
.logs-leave-active {
  transition: all 1s;
}
.logs-enter {
  opacity: 0;
  transform: translateY(-15);
}

.logs-leave-to {
  opacity: 0;
  transform: translateY(-15);
}
</style>

<template>
  <div class="space-y-2">
    <div v-if="$apollo.loading" class="flex flex-row justify-center">
      <Loader  />
    </div>
    <div class="text-center" v-else-if="allServers.length === 0">
      There are no servers assigned to your account.
    </div>
    <ServerListItem
      v-else
      v-for="server in allServers"
      :key="server.serverId"
      :name="server.description"
      :server_id="server.serverId"
      :up="server.state.running"
      :status_time="33345"
      :cpu="server.state.cpuUsage * 100"
      :memory="bytesToString(server.state.memoryUsage)"
      :host="server.host"
      :port="server.port"
      :sftpPort="server.sftpPort"
    />
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import allServers from '~/apollo/queries/allServers.gql'
import { bytesToString } from '~/helpers'

export default Vue.extend({
  methods: {
    bytesToString: bytesToString,
  },
  apollo: {
    allServers: {
      prefetch: true,
      query: allServers,
      pollInterval: 5000,
      refetchWritePolicy: "overwrite"
    },
  },
  middleware: ["auth"]
})
</script>

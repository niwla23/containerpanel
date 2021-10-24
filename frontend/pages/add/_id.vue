<template>
  <div class="space-y-2 md:p-32 md:pt-2">
    <TextInput
      v-model="description"
      placeholder="My MC Server"
      description="Description"
      name="description"
    />
    <TextInput
      v-model="port"
      placeholder="31001"
      description="Port"
      name="port"
    />
    <TextInput
      v-model="sftpPort"
      placeholder="32001"
      description="SFTP Port"
      name="sftp_port"
    />
    <div>
      <label for="allowed_users"
        >Users allowed to manage this server (admins and your account are added
        automatically)</label
      >
      <select
        name="allowed_users"
        class="pl-2 bg-gray-800 rounded-md w-full p-2"
        required
        id="allowed_users"
        v-model="allowed_users"
        multiple
      >
        <option v-for="user in allUsers" :key="user.username" :value="user.username">
          {{ user.username }}
        </option>
      </select>
    </div>
    <section>
      <TextInput
        v-for="option in template ? template.options : []"
        :key="option.key"
        :placeholder="option.value"
        :description="option.key"
        :help="option.description"
        v-model="options_values[option.key]"
        :name="option.key"
      />
    </section>
    <div class="h-2" />
    <button @click="submit" class="bg-green-600 p-2 rounded-md w-full">
      Create Server
    </button>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import createServerMutation from '~/apollo/mutations/createServer.gql'
import templateQuery from '~/apollo/queries/template.gql'
import allUsersQuery from '~/apollo/queries/allUsers.gql'
import { createNameFromDescription } from '~/helpers'

type CreateServerResponse = {
  data: {
    createServer: {
      server: {
        serverId: string
        __typename: 'ServerType'
      }
      __typename: 'CreateServerMutation'
    }
  }
}

export default Vue.extend({
  data: () => {
    return {
      description: '',
      port: '',
      sftpPort: '',
      allowed_users: [],
      options_values: {},
    }
  },
  methods: {
    submit() {
      let options_processed = []
      for (const [key, value] of Object.entries(this.options_values)) {
        options_processed.push({
          key: key,
          value: value,
        })
      }

      this.$apollo
        .mutate({
          mutation: createServerMutation,
          variables: {
            name: createNameFromDescription(this.description),
            description: this.description,
            port: this.port,
            sftpPort: this.sftpPort,
            allowedUsers: this.allowed_users,
            template: this.$route.params.id,
            options: options_processed,
          },
        })
        .then((response: CreateServerResponse) => {
          this.$router.push(
            `/server/${response.data.createServer.server.serverId}`
          )
        })
    },
  },
  apollo: {
    template: {
      prefetch: true,
      query: templateQuery,
      variables() {
        return {
          templateName: this.$route.params.id,
        }
      },
    },
    allUsers: {
      prefetch: true,
      query: allUsersQuery,
    },
  },
})
</script>

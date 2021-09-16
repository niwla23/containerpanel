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
      <label for="allowed_users">Users allowed to manage this server (admins and your account are added automatically)</label>
      <select
        name="allowed_users"
        class="pl-2 bg-gray-800 rounded-md w-full p-2"
        required
        id="allowed_users"
        v-model="allowed_users"
        multiple
      >
        <option value="1">niwla23</option>
        <option value="2">admin</option>
      </select>
    </div>
    <div class="h-2" />
    <button class="bg-green-600 p-2 rounded-md w-full">Create Server</button>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data: () => {
    return {
      description: '',
      port: '',
      sftpPort: '',
      allowed_users: []
    }
  },
})
</script>

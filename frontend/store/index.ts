export const state = () => ({
  username: "loading..."
})

export const mutations = {
  setUsername(state, username: string) {
    state.username = username
  }
}

export const actions = {
  async fetchUsername ({ commit }) {
      let user = await this.$axios.$get('/username');
      commit("setUsername", user)
  }
}
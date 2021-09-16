import { mount } from '@vue/test-utils'
import Loader from '~/components/Loader.vue'


describe('Loader', () => {
  test('is a Vue instance', () => {
    const wrapper = mount(Loader)
    expect(wrapper.vm).toBeTruthy()
  })
})

import { mount } from '@vue/test-utils'
import PingDot from '~/components/PingDot.vue'


describe('PingDot', () => {
    test('is a Vue instance', () => {
        const wrapper = mount(PingDot)
        expect(wrapper.vm).toBeTruthy()
    })
    test('is green when prop is up', () => {
        const wrapper = mount(PingDot, {
            propsData: {
                up: true
            }
        })
        expect(wrapper.html()).toContain('bg-green-600')
    })
    test('is red when prop is down', () => {
        const wrapper = mount(PingDot, {
            propsData: {
                up: false
            }
        })
        expect(wrapper.html()).toContain('bg-red-600')
    })
})

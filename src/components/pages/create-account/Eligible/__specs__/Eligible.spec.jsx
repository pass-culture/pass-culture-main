import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import { act } from 'react-dom/test-utils'

import Eligible from '../Eligible'

jest.mock('../../../../../utils/config', () => ({
  ID_CHECK_URL: 'https://id-check-url/premiere-page',
}))
jest.mock('../../utils/recaptcha', () => ({
  getReCaptchaToken() {
    return Promise.resolve('recaptcha-token')
  },
}))

describe('eligible page', () => {
  describe('on render', () => {
    it('should display the text "Tu es éligible !"', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )

      // then
      const eligibleText = wrapper.find({ children: 'Tu es éligible !' })
      expect(eligibleText).toHaveLength(1)
    })

    it('should display a go back home link', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )

      // then
      const goBackHomeLink = wrapper.find('a[href="/beta"]')
      expect(goBackHomeLink).toHaveLength(1)
    })

    it('should display an enabled button to start inscription', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )

      // then
      const button = wrapper.find('button[type="button"]')
      expect(button).toHaveLength(1)
      expect(button.prop('disabled')).toBe(false)
      expect(button.text()).toBe('Commencer l’inscription')
    })
  })

  describe('on confirmation click', () => {
    beforeEach(() => {
      delete window.location
      window.location = { href: 'inital-url' }
    })
    it('should redirect on id-check page with correct token', async () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )
      const confirmationButton = wrapper.find('button[type="button"]')

      // when
      await confirmationButton.invoke('onClick')()

      // then
      expect(window.location.href).toBe(
        'https://id-check-url/premiere-page?licence_token=recaptcha-token'
      )
    })

    it('should disable the button to start inscription', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )
      const button = wrapper.find('button[type="button"]')

      // when
      act(() => {
        button.invoke('onClick')()
      })
      wrapper.update()

      // then
      expect(wrapper.find('button[type="button"]').prop('disabled')).toBe(true)
    })
  })
})

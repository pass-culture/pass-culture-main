import { mount } from 'enzyme'
import React from 'react'
import Eligible from '../Eligible'
import { MemoryRouter } from 'react-router'

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

    it('should display a sign up button that redirects to a signup portal', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <Eligible />
        </MemoryRouter>
      )

      // then
      const signUpButton = wrapper.find('a[href="https://google.com"]')
      expect(signUpButton).toHaveLength(1)
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
  })

  describe('on confirmation click', () => {
    it('should redirect on id-check page with correct token', async () => {
      // given
      delete window.location
      window.location = { href: 'inital-url' }
      const wrapper = mount(<Eligible />)
      const confirmationButton = wrapper.find('button[type="submit"]')

      // when
      await confirmationButton.simulate('click')

      // then
      expect(window.location.href).toBe(
        'https://id-check-url/premiere-page?licence_token=recaptcha-token'
      )
    })
  })
})

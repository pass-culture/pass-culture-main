import React from 'react'
import { mount } from 'enzyme'

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

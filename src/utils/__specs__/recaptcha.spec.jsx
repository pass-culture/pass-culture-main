import React from 'react'
import { mount } from 'enzyme'
import { useReCaptchaScript } from '../recaptcha'

jest.mock('../config', () => ({
  RECAPTCHA_SITE_KEY: 'recaptcha-site-key',
}))

describe('useReCaptchaScript', () => {
  beforeEach(() => {
    document.querySelectorAll('script').forEach(script => script.remove())
  })

  it('should append script tag on first render', () => {
    // Given
    const ExampleComponent = () => {
      useReCaptchaScript()
      return null
    }

    // When
    mount(<ExampleComponent />)

    // Then
    const scriptTag = document.querySelector(
      'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
    )
    expect(scriptTag).not.toBeNull()
  })

  it('should remove script tag on unMount', () => {
    // Given
    const ExampleComponent = () => {
      useReCaptchaScript()
      return null
    }

    // When
    const wrapper = mount(<ExampleComponent />)
    wrapper.unmount()

    // Then
    const scriptTag = document.querySelector(
      'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
    )
    expect(scriptTag).toBeNull()
  })
})

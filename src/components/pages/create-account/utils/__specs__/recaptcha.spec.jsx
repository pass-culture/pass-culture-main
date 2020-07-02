import React from 'react'
import { useReCaptchaScript } from '../recaptcha'
import { mount } from 'enzyme'

jest.mock('../../../../../utils/config', () => ({
  RECAPTCHA_SITE_KEY: 'recaptcha-site-key',
}))

function cleanScriptTags() {
  document.querySelectorAll('script').forEach(script => script.remove())
}

describe('useReCaptchaScript', () => {
  beforeEach(() => {
    cleanScriptTags()
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

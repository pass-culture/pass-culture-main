import { render } from '@testing-library/react'
import React from 'react'

import { initReCaptchaScript } from '../recaptcha'

jest.mock('../config', () => ({
  RECAPTCHA_SITE_KEY: 'recaptcha-site-key',
}))

describe('initReCaptchaScript', () => {
  beforeEach(() => {
    document.querySelectorAll('script').forEach(script => script.remove())
  })

  it('should append script tag on first render', () => {
    // Given
    const ExampleComponent = () => {
      initReCaptchaScript()
      return null
    }

    // When
    render(<ExampleComponent />)

    // Then
    const scriptTag = document.querySelector(
      'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
    )
    expect(scriptTag).not.toBeNull()
  })
})

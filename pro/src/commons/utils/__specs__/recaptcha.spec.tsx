import { render } from '@testing-library/react'

import { initReCaptchaScript } from '../recaptcha'

vi.mock('../config', () => ({ RECAPTCHA_SITE_KEY: 'recaptcha-site-key' }))

describe('initReCaptchaScript', () => {
  beforeEach(() => {
    document.querySelectorAll('script').forEach((script) => {
      script.remove()
    })
  })

  it('should append script tag on first render', () => {
    const ExampleComponent = () => {
      initReCaptchaScript()
      return null
    }

    render(<ExampleComponent />)

    const scriptTag = document.querySelector(
      'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
    )
    expect(scriptTag).not.toBeNull()
  })
})

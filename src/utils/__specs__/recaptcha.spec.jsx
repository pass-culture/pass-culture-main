import { mount } from 'enzyme'
import React, { PureComponent } from 'react'

import { initReCaptchaScript, destroyReCaptchaScript } from '../recaptcha'

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
    mount(<ExampleComponent />)

    // Then
    const scriptTag = document.querySelector(
      'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
    )
    expect(scriptTag).not.toBeNull()
  })

  it('should remove script tag on unMount', () => {
    // Given
    class ExampleComponent extends PureComponent {
      constructor(props) {
        super(props)
        initReCaptchaScript()
      }

      componentWillUnmount() {
        destroyReCaptchaScript()
      }

      render() {
        return <div />
      }
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

  it('should not crash if element is not found', () => {
    // Given
    /* eslint-disable react/no-multi-comp */
    class ExampleComponent extends PureComponent {
      componentWillUnmount() {
        destroyReCaptchaScript()
      }

      render() {
        return <div />
      }
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

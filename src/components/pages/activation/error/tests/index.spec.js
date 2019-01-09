// jest --env=jsdom ./src/components/pages/activation/tests/ActivationError --watch
import React from 'react'
import { render } from 'enzyme'
import ActivationError from '../index'

describe('src | components | pages | activation | ActivationError', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = render(<ActivationError />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should contains a link with an href attributes equal to mailto:obfuscated', () => {
    // when
    const wrapper = render(<ActivationError />)
    const element = wrapper.find('#activation-error-contact-us')

    // then
    expect(element.prop('href')).toEqual('mailto:obfuscated')
  })
})

import React from 'react'
import { mount } from 'enzyme/build'
import { App } from '../App'

describe('src | App', () => {
  it('should render children components', () => {
    // Given
    const props = { modalOpen: false }

    // When
    const wrapper = mount(
      <App {...props}>
        <p>
          {'Sub component'}
        </p>
      </App>
    )

    // Then
    expect(wrapper.text()).toBe('Sub component')
  })
})

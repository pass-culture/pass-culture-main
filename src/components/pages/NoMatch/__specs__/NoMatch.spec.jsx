import React from 'react'
import { mount } from 'enzyme'
import NoMatch from '../NoMatch'
import { MemoryRouter } from 'react-router'

describe('src | components | pages | NoMatch', () => {
  it('should displays a sentence that says the user is on the wrong path', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <NoMatch />
      </MemoryRouter>
    )

    // then
    const sentence = wrapper.find('.subtitle')
    const timer = wrapper.find('.redirection-info')
    expect(sentence).toHaveLength(1)
    expect(timer).toHaveLength(1)
    expect(timer.text()).toBe('Vous allez être redirigé dans 5 secondes')
  })
})

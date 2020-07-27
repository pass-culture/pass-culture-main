import { mount } from 'enzyme'
import React from 'react'

import { MemoryRouter } from 'react-router'
import NotMatch from '../NotMatch'

describe('notMatch', () => {
  beforeEach(() => {
    window.history.pushState({}, 'Fake title', '/fake-url')
  })

  it('should displays a sentence that says the user is on the wrong path', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <NotMatch />
      </MemoryRouter>
    )

    // then
    const sentence = wrapper.find('.not-match-subtitle')
    const timer = wrapper.find('.redirection-info')
    expect(sentence).toHaveLength(1)
    expect(timer).toHaveLength(1)
    expect(timer.text()).toBe('Tu vas être redirigé dans 5 secondes...')
  })
})

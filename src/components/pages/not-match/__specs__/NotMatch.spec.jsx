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
    const sentence = wrapper.find({ children: '404 Not found /fake-url' })
    const timer = wrapper.find({
      children: 'Vous allez être automatiquement redirigé dans 5 secondes.',
    })
    expect(sentence).toHaveLength(1)
    expect(timer).toHaveLength(1)
  })
})

import { mount } from 'enzyme'
import React from 'react'

import { MemoryRouter } from 'react-router'
import NoItems from '../NoItems'

describe('src | components | NoItems', () => {
  it('should display a sentence', () => {
    //given
    const props = {
      sentence: 'Fake sentence',
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NoItems {...props} />
      </MemoryRouter>,
    )

    // then
    const sentence = wrapper.find({ children: props.sentence })
    expect(sentence).toHaveLength(1)
  })

  it('should display a link to home page', () => {
    //given
    const props = {
      sentence: 'Fake sentence',
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NoItems {...props} />
      </MemoryRouter>,
    )

    // Then
    const link = wrapper.find('a')
    expect(link.prop('href')).toBe('/')
    expect(link.text()).toBe('Lance-toi !')
  })
})

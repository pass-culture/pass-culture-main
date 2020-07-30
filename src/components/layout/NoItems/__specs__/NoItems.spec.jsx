import { mount } from 'enzyme'
import React from 'react'

import { MemoryRouter } from 'react-router'
import NoItems from '../NoItems'

describe('src | components | NoItems', () => {
  it('should display a link and a sentence', () => {
    //given
    const props = {
      sentence: 'Fake sentence',
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NoItems {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find('a')
    const sentence = wrapper.find({ children: props.sentence })
    expect(link.prop('href')).toBe('/decouverte')
    expect(link.text()).toBe('Lance-toi !')
    expect(sentence).toHaveLength(1)
  })
})

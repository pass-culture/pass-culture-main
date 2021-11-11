import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import BackLink from '../BackLink'

describe('src | components | BackLink', () => {
  it('should display a link and an image', () => {
    // Given
    const props = {
      actionOnClick: jest.fn(),
      backTitle: 'Fake title',
      backTo: '/fake-url',
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <BackLink {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find('a')
    const image = wrapper.find('img')
    expect(link.prop('href')).toBe('/fake-url')
    expect(link.prop('onClick')).toStrictEqual(expect.any(Function))
    expect(image.prop('alt')).toBe('Fake title')
    expect(image.prop('src')).toBe('http://localhost/icons/ico-back.svg')
  })
})

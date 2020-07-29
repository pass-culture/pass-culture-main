import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import Icon from '../../../../../layout/Icon/Icon'
import Cover from '../Cover'

describe('src | components | Cover', () => {
  let props

  beforeEach(() => {
    props = {
      img: 'https://www.link-to-my-image.com',
      diplay: ''
    }
  })

  it('should render an image for the Cover', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <Cover {...props} />
      </MemoryRouter>,
    )

    // Then
    const image = wrapper.find('img').at(0)
    expect(image.prop('src')).toBe('https://www.link-to-my-image.com')
  })

  it('should render a swipe icon on top of the image', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <Cover {...props} />
      </MemoryRouter>,
    )

    // Then
    const icon = wrapper.find(Icon)
    expect(icon.prop('svg')).toBe('ico-swipe-tile')
  })
})

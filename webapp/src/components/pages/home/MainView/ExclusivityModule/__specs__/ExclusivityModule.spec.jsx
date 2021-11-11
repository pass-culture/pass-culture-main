import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import ExclusivityModule from '../ExclusivityModule'
import { Link } from 'react-router-dom'
import ExclusivityPane from '../../domain/ValueObjects/ExclusivityPane'

describe('src | components | ExclusivityModule', () => {
  let props

  beforeEach(() => {
    props = {
      module: new ExclusivityPane({
        alt: 'my alt text',
        image: 'https://www.link-to-my-image.com',
        offerId: 'AE'
      })
    }
  })

  it('should render a link to the offer details', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <ExclusivityModule {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find(Link)
    expect(link.prop('to')).toBe('/accueil/details/AE')
  })

  it('should render an image with the provided asset and alternative text', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <ExclusivityModule {...props} />
      </MemoryRouter>
    )

    // then
    const image = wrapper.find('img')
    expect(image.prop('alt')).toBe('my alt text')
    expect(image.prop('src')).toBe('https://www.link-to-my-image.com')
  })

  it('should not render an image when not provided', () => {
    // given
    props.module.image = null

    // when
    const wrapper = mount(
      <MemoryRouter>
        <ExclusivityModule {...props} />
      </MemoryRouter>
    )

    // then
    expect(wrapper.find('section')).toHaveLength(0)
  })
})

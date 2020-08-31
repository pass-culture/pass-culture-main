import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import BusinessModule from '../BusinessModule'
import Icon from '../../../../../layout/Icon/Icon'
import BusinessPane from '../../domain/ValueObjects/BusinessPane'

describe('src | components | BusinessModule', () => {
  let props

  beforeEach(() => {
    props = {
      module: new BusinessPane({
        firstLine: 'my first line',
        image: 'https://www.link-to-my-image.com',
        secondLine: 'my second line',
        url: 'https://www.google.fr',
      }),
    }
  })

  it('should render a link to the provided url', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <BusinessModule {...props} />
      </MemoryRouter>,
    )

    // then
    const link = wrapper.find('a')
    expect(link.prop('href')).toBe(props.module.url)
    expect(link.prop('rel')).toBe('noopener noreferrer')
    expect(link.prop('target')).toBe('_blank')
  })

  it('should render an image with the provided asset', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <BusinessModule {...props} />
      </MemoryRouter>,
    )

    // then
    const image = wrapper.find('img').at(0)
    expect(image.prop('alt')).toBe('')
    expect(image.prop('src')).toBe(props.module.image)
  })

  it('should render two lines with the provided text inputs', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <BusinessModule {...props} />
      </MemoryRouter>,
    )

    // then
    const firstLine = wrapper.find({ children: props.module.firstLine })
    expect(firstLine).toHaveLength(1)
    const secondLine = wrapper.find({ children: props.module.secondLine })
    expect(secondLine).toHaveLength(1)
  })

  it('should render an Icon with the proper svg', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <BusinessModule {...props} />
      </MemoryRouter>,
    )

    // then
    const icon = wrapper.find(Icon)
    expect(icon.prop('svg')).toBe('ico-arrow-next')
  })

  it('should not render component when no image', () => {
    // given
    props.module.image = null

    // when
    const wrapper = mount(
      <MemoryRouter>
        <BusinessModule {...props} />
      </MemoryRouter>,
    )

    // then
    expect(wrapper.find('section')).toHaveLength(0)
  })
})

import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import Icon from '../../../../../layout/Icon/Icon'
import SeeMore from '../SeeMore'

describe('src | components | SeeMore', () => {
  let props

  beforeEach(() => {
    props = {
      layout: 'one-item-medium',
      parameters: {},
    }
  })

  it('should render an icon for the see more component', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>,
    )

    // Then
    const icon = wrapper.find(Icon)
    expect(icon.prop('svg')).toBe('ico-offres-home')
  })

  it('should a "En voir plus" label', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>,
    )

    // Then
    const label = wrapper.find({ children: 'En voir plus' })
    expect(label).toHaveLength(1)
  })
})

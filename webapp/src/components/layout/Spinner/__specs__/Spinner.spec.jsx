import { mount } from 'enzyme'
import React from 'react'

import Spinner from '../Spinner'

describe('src | components | Spinner', () => {
  it('should display an image and label', () => {
    // when
    const wrapper = mount(<Spinner />)

    // then
    const image = wrapper.find('img')
    const label = wrapper.find({ children: 'Chargement' })
    expect(image.prop('src')).toBe('http://localhost/icons/ico-loader-pink.svg')
    expect(label).toHaveLength(1)
  })
})

import { mount } from 'enzyme'
import React from 'react'

import GatewayTimeoutError from '../GatewayTimeoutError'

jest.mock('../../../../../../utils/config', () => ({
  ICONS_URL: 'http://path/to/icons',
}))

describe('src | layout | GatewayTimeoutError', () => {
  it('should render an Icon', () => {
    // When
    const wrapper = mount(<GatewayTimeoutError />)

    // Then
    const image = wrapper.find('img')
    expect(image.prop('alt')).toBe('')
    expect(image.prop('src')).toBe('http://path/to/icons/ico-people.svg')
  })

  it('should have a title', () => {
    // When
    const wrapper = mount(<GatewayTimeoutError />)

    // Then
    expect(wrapper.find({ children: 'Il y a foule !' })).toHaveLength(1)
  })

  it('should have a body text', () => {
    // When
    const wrapper = mount(<GatewayTimeoutError />)

    // Then
    expect(wrapper.find({ children: 'Vous êtes très nombreux à vouloir' })).toHaveLength(1)
    expect(wrapper.find({ children: 'accéder cette page.' })).toHaveLength(1)
    expect(wrapper.find({ children: 'Reviens un peu plus tard.' })).toHaveLength(1)
  })
})

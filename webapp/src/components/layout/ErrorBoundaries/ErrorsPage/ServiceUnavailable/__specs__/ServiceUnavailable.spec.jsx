import { mount } from 'enzyme'
import React from 'react'

import ServiceUnavailable from '../ServiceUnavailable'

jest.mock('../../../../../../utils/config', () => ({
  ICONS_URL: 'http://path/to/icons',
}))

describe('src | layout | ServiceUnavailable', () => {
  it('should render an Icon', () => {
    // When
    const wrapper = mount(<ServiceUnavailable />)

    // Then
    const image = wrapper.find('img')
    expect(image.prop('alt')).toBe('')
    expect(image.prop('src')).toBe('http://path/to/icons/logo-error.svg')
  })

  it('should have a title', () => {
    // When
    const wrapper = mount(<ServiceUnavailable />)

    // Then
    expect(wrapper.find({ children: 'Oops !' })).toHaveLength(1)
  })

  it('should have a body text', () => {
    // When
    const wrapper = mount(<ServiceUnavailable />)

    // Then
    expect(wrapper.find({ children: 'Une erreur s’est produite pendant' })).toHaveLength(1)
    expect(wrapper.find({ children: 'le chargement des offres.' })).toHaveLength(1)
  })

  it('should reload the page when the retry link is clicked', () => {
    // When
    const wrapper = mount(<ServiceUnavailable />)

    // Then
    const link = wrapper.find('a').find({ children: 'Réessayer' })
    expect(link.prop('href')).toBe('/')
  })
})

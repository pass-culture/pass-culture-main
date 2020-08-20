import { mount } from 'enzyme'
import React from 'react'

import AnyError from '../AnyError'

describe('src | layout | anyError', () => {
  it('should render an Icon', () => {
    // When
    const wrapper = mount(<AnyError />)

    // Then
    const image = wrapper.find('img')
    expect(image.prop('alt')).toBe('')
    expect(image.prop('src')).toBe('http://localhost/icons/ico-maintenance.svg')
  })

  it('should have a title', () => {
    // When
    const wrapper = mount(<AnyError />)

    // Then
    expect(wrapper.find({ children: 'Oh non !' })).toHaveLength(1)
  })

  it('should have a body text', () => {
    // When
    const wrapper = mount(<AnyError />)

    // Then
    expect(wrapper.find({ children: 'Une erreur s’est produite pendant' })).toHaveLength(1)
    expect(wrapper.find({ children: 'le chargement de la page.' })).toHaveLength(1)
  })

  it('should reload the page when the retry link is clicked', () => {
    // When
    const wrapper = mount(<AnyError />)

    // Then
    const link = wrapper.find('a').find({ children: 'Réessayer' })
    expect(link.prop('href')).toBe('/')
  })
})

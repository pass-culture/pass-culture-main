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

  it('should have a retry button', () => {
    // When
    const wrapper = mount(<AnyError />)

    // Then
    expect(wrapper.find('button').find({ children: 'Réessayer' })).toHaveLength(1)
  })

  it('should refresh the page when the retry button is clicked', () => {
    // Given
    Object.defineProperty(window.location, 'reload', {
      writable: true,
      value: jest.fn(),
    })
    const wrapper = mount(<AnyError />)
    const button = wrapper.find('button').find({ children: 'Réessayer' })

    // When
    button.invoke('onClick')()

    // Then
    expect(window.location.reload).toHaveBeenCalledWith()
  })
})

import { mount } from 'enzyme'
import Icon from '../../../../layout/Icon/Icon'
import ErrorPage from '../ErrorPage'
import React from 'react'

describe('errorPage', () => {
  let props

  beforeEach(() => {
    props = {
      refreshPage: jest.fn(),
    }
  })

  it('should render an Icon', () => {
    // When
    const wrapper = mount(<ErrorPage {...props} />)

    // Then
    expect(wrapper.find(Icon)).toHaveLength(1)
  })

  it('should have a title', () => {
    // When
    const wrapper = mount(<ErrorPage {...props} />)

    // Then
    expect(wrapper.find({ children: 'Oh non !' })).toHaveLength(1)
  })

  it('should have a body text', () => {
    // When
    const wrapper = mount(<ErrorPage {...props} />)

    // Then
    expect(wrapper.find({ children: 'Une erreur s’est produite pendant' })).toHaveLength(1)
    expect(wrapper.find({ children: 'le chargement de la page.' })).toHaveLength(1)
  })

  it('should have a retry button', () => {
    // When
    const wrapper = mount(<ErrorPage {...props} />)

    // Then
    expect(wrapper.find('button').find({ children: 'Réessayer' })).toHaveLength(1)
  })

  it('should refresh the page when the retry button is clicked', () => {
    // Given
    const wrapper = mount(<ErrorPage {...props} />)

    // When
    const button = wrapper.find('button').find({ children: 'Réessayer' })
    button.invoke('onClick')()

    // Then
    expect(props.refreshPage).toHaveBeenCalledWith()
  })
})

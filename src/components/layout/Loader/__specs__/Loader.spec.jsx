import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import Loader from '../Loader'

describe('layout | Loader', () => {
  let props

  beforeEach(() => {
    props = {
      hasError: false,
      isEmpty: false,
      isLoading: false,
      match: {
        params: {
          mediationId: 'MEFA',
        },
      },
      hasError500: false,
    }
  })

  it('should display error message and button when status code is 500', () => {
    // Given
    const history = createBrowserHistory()
    props.hasError = true
    props.hasError500 = true

    // When
    const wrapper = mount(
      <Router history={history}>
        <Loader {...props} />
      </Router>
    )

    // Then
    const title = wrapper.find({ children: 'Oops !' })
    const message = wrapper.find({
      children: 'Une erreur s’est produite pendant le chargement des offres.',
    })
    const refresh = wrapper.find('button').find({ children: 'Réessayer' })
    expect(title).toHaveLength(1)
    expect(message).toHaveLength(1)
    expect(refresh).toHaveLength(1)
  })

  it('should refresh the page when click on the button', () => {
    // Given
    const mockLocation = jest.spyOn(location, 'reload')
    const history = createBrowserHistory()
    props.hasError = true
    props.hasError500 = true
    const wrapper = mount(
      <Router history={history}>
        <Loader {...props} />
      </Router>
    )

    // When
    wrapper
      .find('button')
      .find({ children: 'Réessayer' })
      .simulate('click')

    // Then
    expect(mockLocation).toHaveBeenCalledTimes(1)
  })
})

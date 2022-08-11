import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import type { Store } from 'redux'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'

import VenueCreation from '../VenueCreation'

const renderVenueCreation = async (store: Store) => {
  const history = createBrowserHistory()
  render(
    <Provider store={store}>
      <Router history={history}>
        <VenueCreation />
      </Router>
    </Provider>
  )
}

jest.mock('new_components/VenueForm', () => {
  return {
    ...jest.requireActual('new_components/VenueForm'),
    setDefaultInitialFormValues: jest.fn().mockImplementation(() => {
      return { publicName: 'Cinéma des iles' }
    }),
  }
})

describe('route VenueCreation', () => {
  let currentUser: SharedCurrentUserResponseModel
  let store: Store

  beforeEach(() => {
    currentUser = {
      firstName: 'John',
      dateCreated: '2022-07-29T12:18:43.087097Z',
      email: 'john@do.net',
      id: '1',
      isAdmin: false,
      isEmailValidated: true,
      roles: [],
    }
    store = configureTestStore({
      user: {
        initialized: true,
        currentUser,
      },
    })
  })
  it('should display venue edition screen with initial values', async () => {
    // When
    renderVenueCreation(store)

    // Then
    const venuePublicName = await screen.findByText('Cinéma des iles')
    expect(venuePublicName).toBeInTheDocument()
  })
})

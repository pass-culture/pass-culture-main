import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'

import VenueCreation from '../VenueCreation'

const renderVenueCreation = async (offererId: string, store: Store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[`/structures/${offererId}/lieux/creation`]}
      >
        <Route exact path={'/structures/:offererId/lieux/creation'}>
          <VenueCreation />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    fetchVenueLabels: jest.fn(),
    getOfferer: jest.fn(),
    getVenueTypes: jest.fn(),
  },
}))

describe('route VenueCreation', () => {
  let currentUser: SharedCurrentUserResponseModel
  let store: Store
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    currentUser = {
      firstName: 'John',
      dateCreated: '2022-07-29T12:18:43.087097Z',
      email: 'john@do.net',
      id: '1',
      nonHumanizedId: '1',
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
    offerer = {
      id: 'ABCD',
    } as GetOffererResponseModel

    jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    jest.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
  })
  it('should display venue form screen with creation title', async () => {
    // When
    await renderVenueCreation(offerer.id, store)

    // Then
    const venueCreationTitle = await screen.findByRole('heading', {
      name: 'Création d’un lieu',
    })
    expect(venueCreationTitle).toBeInTheDocument()
  })
})

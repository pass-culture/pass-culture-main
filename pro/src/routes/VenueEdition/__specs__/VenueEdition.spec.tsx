import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'
import type { Store } from 'redux'

import '@testing-library/jest-dom'

import { api } from 'apiClient/api'
import {
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'

import VenueEdition from '../VenueEdition'

const renderVenueEdition = async (venueId: string, store: Store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[`/venueEdition/${venueId}`]}>
        <Route exact path={'/accueil'}>
          <h1>Home</h1>
        </Route>
        <Route exact path={'/venueEdition/:venueId'}>
          <VenueEdition />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    getVenue: jest.fn(),
  },
}))

describe('route VenueEdition', () => {
  let currentUser: SharedCurrentUserResponseModel
  let store: Store
  let venue: GetVenueResponseModel

  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      publicName: 'USER',
    } as SharedCurrentUserResponseModel

    venue = {
      id: 'AE',
      publicName: 'Cinéma des iles',
    } as GetVenueResponseModel
    store = configureTestStore({
      user: {
        initialized: true,
        currentUser,
      },
    })

    jest.spyOn(api, 'getVenue').mockResolvedValue(venue)
  })
  it('should call getVenue and display Venue Edition screen on success', async () => {
    // When
    await renderVenueEdition(venue.id, store)

    // Then
    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(venuePublicName).toBeInTheDocument()
  })

  it('should return to home when not able to get venue informations', async () => {
    jest
      .spyOn(api, 'getVenue')
      .mockRejectedValue('Impossible de récupérer le lieu')
    // When
    await renderVenueEdition(venue.id, store)

    // Then
    const homeTitle = await screen.findByRole('heading', {
      name: 'Home',
    })
    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(homeTitle).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'
import type { Store } from 'redux'

import '@testing-library/jest-dom'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { IProviders, IVenueProviderApi } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import VenueEdition from '../VenueEdition'

const renderVenueEdition = async (
  venueId: string,
  offererId: string,
  store: Store
) => {
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[`/structures/${offererId}/lieux/${venueId}`]}
      >
        <Route exact path={'/accueil'}>
          <h1>Home</h1>
        </Route>
        <Route exact path={'/structures/:offererId/lieux/:venueId'}>
          <VenueEdition />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    fetchVenueLabels: jest.fn(),
    getVenue: jest.fn(),
    getOfferer: jest.fn(),
    getVenueTypes: jest.fn(),
  },
}))

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

describe('route VenueEdition', () => {
  let currentUser: SharedCurrentUserResponseModel
  let store: Store
  let venue: GetVenueResponseModel
  let venueProviders: IVenueProviderApi[]
  let providers: IProviders[]
  let offerer: GetOffererResponseModel

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

    venueProviders = [
      {
        id: 'BY',
        idAtProviders: null,
        dateModifiedAtLastProvider: '2022-09-19T12:01:18.708794Z',
        isActive: true,
        isFromAllocineProvider: false,
        lastProviderId: null,
        lastSyncDate: null,
        nOffers: 0,
        providerId: 'BY',
        venueId: 'DE',
        venueIdAtOfferProvider: 'cdsdemorc1',
        provider: {
          name: 'Ciné Office',
          enabledForPro: true,
          id: 'BY',
          isActive: true,
          localClass: 'CDSStocks',
        },
        quantity: 0,
        isDuo: true,
        price: 0,
      },
    ]

    providers = [
      {
        enabledForPro: true,
        id: 'AB',
        isActive: true,
        name: 'name',
      },
    ] as IProviders[]

    offerer = {
      id: 'ABCD',
    } as GetOffererResponseModel
    store = configureTestStore({
      user: {
        initialized: true,
        currentUser,
      },
    })

    jest.spyOn(api, 'getVenue').mockResolvedValue(venue)
    jest.spyOn(pcapi, 'loadProviders').mockResolvedValue(providers)
    jest.spyOn(pcapi, 'loadVenueProviders').mockResolvedValue(venueProviders)
    jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    jest.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
  })
  it.only('should call getVenue and display Venue Form screen on success', async () => {
    // When
    await renderVenueEdition(venue.id, offerer.id, store)

    // Then
    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledWith('AE')
    expect(venuePublicName).toBeInTheDocument()
  })

  it('should return to home when not able to get venue informations', async () => {
    jest
      .spyOn(api, 'getVenue')
      .mockRejectedValue('Impossible de récupérer le lieu')
    // When
    await renderVenueEdition(venue.id, offerer.id, store)

    // Then
    const homeTitle = await screen.findByRole('heading', {
      name: 'Home',
    })
    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(homeTitle).toBeInTheDocument()
  })
})

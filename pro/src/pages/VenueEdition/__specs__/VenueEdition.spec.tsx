import { screen } from '@testing-library/react'
import React from 'react'
import { Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { IProviders } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueEdition from '../VenueEdition'

const renderVenueEdition = (venueId: string, offererId: string) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        id: 'EY',
        isAdmin: false,
        publicName: 'USER',
      },
    },
  }

  return renderWithProviders(
    <>
      <Route exact path={'/accueil'}>
        <h1>Home</h1>
      </Route>
      <Route exact path={'/structures/:offererId/lieux/:venueId'}>
        <VenueEdition />
      </Route>
    </>,
    {
      storeOverrides,
      initialRouterEntries: [`/structures/${offererId}/lieux/${venueId}`],
    }
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    fetchVenueLabels: jest.fn(),
    getVenue: jest.fn(),
    getOfferer: jest.fn(),
    getVenueTypes: jest.fn(),
    listVenueProviders: jest.fn(),
  },
}))

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

describe('route VenueEdition', () => {
  let venue: GetVenueResponseModel
  let venueProviders: VenueProviderResponse[]
  let providers: IProviders[]
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    venue = {
      id: 'AE',
      publicName: 'Cinéma des iles',
    } as GetVenueResponseModel

    venueProviders = [
      {
        id: 'BY',
        idAtProviders: undefined,
        dateModifiedAtLastProvider: '2022-09-19T12:01:18.708794Z',
        isActive: true,
        isFromAllocineProvider: false,
        lastProviderId: undefined,
        lastSyncDate: undefined,
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
        fieldsUpdated: [],
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

    jest.spyOn(api, 'getVenue').mockResolvedValue(venue)
    jest.spyOn(pcapi, 'loadProviders').mockResolvedValue(providers)
    jest
      .spyOn(api, 'listVenueProviders')
      .mockResolvedValue({ venue_providers: venueProviders })
    jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    jest.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
  })
  it('should call getVenue and display Venue Form screen on success', async () => {
    // When
    renderVenueEdition(venue.id, offerer.id)

    // Then
    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledWith('AE')
    expect(venuePublicName).toBeInTheDocument()
  })

  it('should return to home when not able to get venue informations', async () => {
    jest.spyOn(api, 'getVenue').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 404,
          body: {
            global: ['error'],
          },
        } as ApiResult,
        ''
      )
    )
    // When
    renderVenueEdition(venue.id, offerer.id)

    // Then
    expect(api.getVenue).toHaveBeenCalledTimes(1)
    const homeTitle = await screen.findByRole('heading', {
      name: 'Home',
    })
    expect(homeTitle).toBeInTheDocument()
  })
})

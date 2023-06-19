import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import * as router from 'react-router-dom'

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

const renderVenueEdition = (venueId: number, offererId: number) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        id: 'EY',
        isAdmin: false,
      },
    },
  }

  return renderWithProviders(
    <Routes>
      <Route
        path="/structures/:offererId/lieux/:venueId"
        element={<VenueEdition />}
      />
      <Route path="/accueil" element={<h1>Home</h1>} />
    </Routes>,
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
    listOffers: jest.fn(),
  },
}))

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: '1234',
    venueId: '12',
  }),
  useNavigate: jest.fn(),
}))

describe('route VenueEdition', () => {
  let venue: GetVenueResponseModel
  let venueProviders: VenueProviderResponse[]
  let providers: IProviders[]
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    venue = {
      id: 'AE',
      nonHumanizedId: 12,
      publicName: 'Cinéma des iles',
      dmsToken: 'dms-token-12345',
    } as GetVenueResponseModel

    venueProviders = [
      {
        id: 1,
        isActive: true,
        isFromAllocineProvider: false,
        lastSyncDate: undefined,
        nOffers: 0,
        venueId: 2,
        venueIdAtOfferProvider: 'cdsdemorc1',
        provider: {
          name: 'Ciné Office',
          hasOffererProvider: false,
          nonHumanizedId: 1,
        },
        quantity: 0,
        isDuo: true,
        price: 0,
      },
    ]

    providers = [
      {
        name: 'name',
      },
    ] as IProviders[]

    offerer = {
      nonHumanizedId: 13,
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
    renderVenueEdition(venue.nonHumanizedId, offerer.nonHumanizedId)

    // Then
    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledWith(12)
    expect(venuePublicName).toBeInTheDocument()
  })

  it('should check none accessibility', async () => {
    jest.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...venue,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      audioDisabilityCompliant: false,
      motorDisabilityCompliant: false,
    })

    renderVenueEdition(venue.nonHumanizedId, offerer.nonHumanizedId)

    await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })

    expect(
      screen.getByLabelText('Non accessible', { exact: false })
    ).toBeChecked()
  })

  it('should not check none accessibility if every accessibility parameters are null', async () => {
    jest.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...venue,
      visualDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      audioDisabilityCompliant: null,
      motorDisabilityCompliant: null,
    })

    renderVenueEdition(venue.nonHumanizedId, offerer.nonHumanizedId)

    await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })

    expect(
      screen.getByLabelText('Non accessible', { exact: false })
    ).not.toBeChecked()
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
    const mockNavigate = jest.fn()
    jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    // When
    renderVenueEdition(venue.nonHumanizedId, offerer.nonHumanizedId)

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))
    // Then
    expect(api.getVenue).toHaveBeenCalledTimes(1)

    expect(mockNavigate).toHaveBeenCalledWith('/accueil')
  })
})

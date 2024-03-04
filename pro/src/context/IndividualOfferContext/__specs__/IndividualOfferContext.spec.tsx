import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import Notification from 'components/Notification/Notification'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import {
  getIndividualOfferFactory,
  getOfferManagingOffererFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualOfferContextProvider,
  IndividualOfferContextProviderProps,
} from '../IndividualOfferContext'

const offerer = getOfferManagingOffererFactory()
const apiOffer: GetIndividualOfferResponseModel = getIndividualOfferFactory()

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

const renderIndividualOfferContextProvider = (
  props?: Partial<IndividualOfferContextProviderProps>
) =>
  renderWithProviders(
    <>
      <IndividualOfferContextProvider
        isUserAdmin={false}
        offerId={String(apiOffer.id)}
        queryOffererId={String(offerer.id)}
        {...props}
      >
        Test
      </IndividualOfferContextProvider>
      <Notification />
    </>
  )

describe('IndividualOfferContextProvider', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(router, 'useLoaderData').mockResolvedValue({ offer: apiOffer })
  })

  it('should initialize context with api when a offerId is given and user is admin', async () => {
    renderIndividualOfferContextProvider({ isUserAdmin: true })

    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(
        null, // validated
        true, // activeOfferersOnly,
        offerer.id // offererId
      )
    })
    expect(api.getCategories).toHaveBeenCalledWith()
  })

  it('should initialize context with api when a offerId is given', async () => {
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(
        null, // validated
        true, // activeOfferersOnly,
        undefined // offererId, undefinded because we need all the venues
      )
    })
    expect(api.getCategories).toHaveBeenCalledWith()
  })

  it('should initialize context with api when no offerId is given', async () => {
    renderIndividualOfferContextProvider({ offerId: undefined })

    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(
        null, // validated
        true, // activeOfferersOnly,
        undefined // offererId, undefinded because we need all the venues
      )
    })
    expect(api.getCategories).toHaveBeenCalledWith()
  })

  it('should display an error when unable to load categories', async () => {
    vi.spyOn(api, 'getCategories').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        { body: { global: ['Une erreur est survenue'] } } as ApiResult,
        ''
      )
    )

    renderIndividualOfferContextProvider()

    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    expect(await screen.findByText(GET_DATA_ERROR_MESSAGE)).toBeInTheDocument()
  })
})

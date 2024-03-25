import { waitFor } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import {
  getOfferManagingOffererFactory,
  getIndividualOfferFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualOfferContextProvider,
  IndividualOfferContextProviderProps,
} from '../IndividualOfferContext'

const offerer = getOfferManagingOffererFactory()
const apiOffer: GetIndividualOfferResponseModel = getIndividualOfferFactory()

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useLoaderData: vi.fn(),
}))

const renderIndividualOfferContextProvider = (
  props?: Partial<IndividualOfferContextProviderProps>
) =>
  renderWithProviders(
    <IndividualOfferContextProvider isUserAdmin={false} {...props}>
      Test
    </IndividualOfferContextProvider>
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

  it('should initialize context with api when a offererId is given and user is admin', async () => {
    renderIndividualOfferContextProvider({
      isUserAdmin: true,
      queryOffererId: String(offerer.id),
    })

    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(
        null, // validated
        true, // activeOfferersOnly,
        offerer.id // offererId
      )
    })
    expect(api.getCategories).toHaveBeenCalled()
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
    expect(api.getCategories).toHaveBeenCalled()
  })
})

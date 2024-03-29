import { waitFor } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IndividualOfferContextProvider } from '../IndividualOfferContext'

const apiOffer: GetIndividualOfferResponseModel = getIndividualOfferFactory()

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useLoaderData: vi.fn(),
}))

const renderIndividualOfferContextProvider = () =>
  renderWithProviders(
    <IndividualOfferContextProvider>Test</IndividualOfferContextProvider>
  )

describe('IndividualOfferContextProvider', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(router, 'useLoaderData').mockResolvedValue({ offer: apiOffer })
  })

  it('should initialize context with api', async () => {
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getCategories).toHaveBeenCalled()
    })
  })
})

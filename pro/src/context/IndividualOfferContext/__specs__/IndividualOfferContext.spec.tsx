import { waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IndividualOfferContextProvider } from '../IndividualOfferContext'

const apiOffer: GetIndividualOfferResponseModel = getIndividualOfferFactory()

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
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  })

  it('should initialize context with api', async () => {
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getCategories).toHaveBeenCalled()
    })
  })
})

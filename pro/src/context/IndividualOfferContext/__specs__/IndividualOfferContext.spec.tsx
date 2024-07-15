import { waitFor } from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IndividualOfferContextProvider } from '../IndividualOfferContext'

const apiOffer: GetIndividualOfferWithAddressResponseModel =
  getIndividualOfferFactory()

const renderIndividualOfferContextProvider = () =>
  renderWithProviders(
    <IndividualOfferContextProvider>Test</IndividualOfferContextProvider>
  )

describe('IndividualOfferContextProvider', () => {
  it('should initialize context with api', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValueOnce(apiOffer)
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getCategories).toHaveBeenCalled()
    })
  })
})

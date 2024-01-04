import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { routesIndividualOfferWizard } from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import {
  GetIndividualOfferFactory,
  offererFactory,
  offerVenueFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import {
  IndividualOfferContextProvider,
  IndividualOfferContextProviderProps,
} from '../IndividualOfferContext'

const offerer = offererFactory()
const apiOffer: GetIndividualOfferResponseModel = GetIndividualOfferFactory()

const renderIndividualOfferContextProvider = (
  props?: Partial<IndividualOfferContextProviderProps>
) =>
  renderWithProviders(
    <IndividualOfferContextProvider
      isUserAdmin
      offerId={String(apiOffer.id)}
      queryOffererId={String(offerer.id)}
      {...props}
    >
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
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  })

  it('should initialize context with api when a offerId is given', async () => {
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(
        null, // validated
        true, // activeOfferersOnly,
        offerer.id // offererId
      )
    })
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).toHaveBeenCalledWith(apiOffer.id)
  })
})

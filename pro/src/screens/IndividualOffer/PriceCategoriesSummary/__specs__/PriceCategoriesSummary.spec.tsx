import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { Events } from 'core/FirebaseEvents/constants'
import { IndividualOffer } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  individualOfferFactory,
  individualOfferSubCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PriceCategoriesSummary } from '../PriceCategoriesSummary'

const mockLogEvent = vi.fn()

const duoSubcategory = individualOfferSubCategoryFactory({ canBeDuo: true })
const renderPriceCategoriesSummary = (offer: IndividualOffer) => {
  const contextValue: IndividualOfferContextValues = {
    offerId: null,
    offer,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [duoSubcategory],
    setOffer: () => {},
    setShouldTrack: () => {},
    setSubcategory: () => {},
    shouldTrack: true,
    showVenuePopin: {},
  }

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <PriceCategoriesSummary />
    </IndividualOfferContext.Provider>
  )
}
describe('StockEventSection', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should render correctly', () => {
    const offer = individualOfferFactory({ subcategoryId: duoSubcategory.id })

    renderPriceCategoriesSummary(offer)

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.getByText(/Accepter les réservations "Duo"/)
    ).toBeInTheDocument()
  })

  it('should render correctly when offer cannot be duo', () => {
    const offer = individualOfferFactory()

    renderPriceCategoriesSummary(offer)

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.queryByText(/Accepter les réservations "Duo"/)
    ).not.toBeInTheDocument()
  })

  it('should track click on modify button', async () => {
    const offer = individualOfferFactory()

    renderPriceCategoriesSummary(offer)

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: false,
        isEdition: true,
        offerId: offer.id,
        to: 'tarifs',
        used: 'RecapLink',
      }
    )
  })
})

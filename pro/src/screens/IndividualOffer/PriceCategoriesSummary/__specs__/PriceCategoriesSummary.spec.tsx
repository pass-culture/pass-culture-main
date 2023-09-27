import { screen } from '@testing-library/react'
import React from 'react'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { IndividualOffer } from 'core/Offers/types'
import {
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferSubCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PriceCategoriesSummaryScreen } from '../PriceCategoriesSummary'

const duoSubcategory = individualOfferSubCategoryFactory({ canBeDuo: true })
const renderPriceCategoriesSummary = (offer: IndividualOffer) => {
  const contextValue: IndividualOfferContextValues =
    individualOfferContextFactory({
      offerId: offer.id,
      offer,
      subCategories: [duoSubcategory],
    })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <PriceCategoriesSummaryScreen />
    </IndividualOfferContext.Provider>
  )
}
describe('StockEventSection', () => {
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
})

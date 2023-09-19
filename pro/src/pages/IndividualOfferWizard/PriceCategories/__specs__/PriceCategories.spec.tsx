import { screen } from '@testing-library/react'
import React from 'react'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories from '../PriceCategories'

const renderOffer = (
  contextOverride?: Partial<IndividualOfferContextValues>
) => {
  const contextValue: IndividualOfferContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    setSubcategory: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <PriceCategories />
    </IndividualOfferContext.Provider>
  )
}

describe('PriceCategories', () => {
  it('should display', () => {
    renderOffer({ offer: individualOfferFactory() })
    expect(screen.getByText('Modifier l’offre')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', () => {
    renderOffer()
    expect(screen.queryByText('Modifier l’offre')).not.toBeInTheDocument()
  })
})

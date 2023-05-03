import { screen } from '@testing-library/react'
import React from 'react'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories from '../PriceCategories'

const renderOffer = (contextOverride?: Partial<IOfferIndividualContext>) => {
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <OfferIndividualContext.Provider value={contextValue}>
      <PriceCategories />
    </OfferIndividualContext.Provider>
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

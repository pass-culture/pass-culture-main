import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PriceCategories } from '../PriceCategories'

const renderOffer = (
  contextOverride?: Partial<IndividualOfferContextValues>
) => {
  const contextValue: IndividualOfferContextValues =
    individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <Routes>
      <Route
        path="/edition/tarifs"
        element={
          <IndividualOfferContext.Provider value={contextValue}>
            <PriceCategories />
          </IndividualOfferContext.Provider>
        }
      />
    </Routes>,
    { initialRouterEntries: ['/edition/tarifs'] }
  )
}

describe('PriceCategories', () => {
  it('should display', () => {
    renderOffer()
    expect(screen.getByText('Modifier l’offre')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', () => {
    renderOffer({ offer: null })
    expect(screen.queryByText('Modifier l’offre')).not.toBeInTheDocument()
  })
})

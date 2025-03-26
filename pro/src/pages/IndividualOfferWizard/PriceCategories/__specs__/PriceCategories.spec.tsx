import { screen } from '@testing-library/react'
import { Routes, Route } from 'react-router-dom'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

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

  it('should render a spinner when the offer is not set', () => {
    renderOffer({ offer: null })
    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })
})

import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferPriceCategories } from './IndividualOfferPriceCategories'

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
            <IndividualOfferPriceCategories />
          </IndividualOfferContext.Provider>
        }
      />
    </Routes>,
    { initialRouterEntries: ['/edition/tarifs'] }
  )
}

describe('IndividualOfferPriceCategories', () => {
  it('should render when the offer is set', () => {
    renderOffer()
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
  })

  it('should not render anything but a spinner when the offer is set', () => {
    renderOffer({ offer: null })
    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })
})

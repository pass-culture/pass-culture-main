import { screen } from '@testing-library/react'

import { OfferStatus } from 'apiClient/v1'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { StocksCalendarSummaryScreen } from './StocksCalendarSummaryScreen'

describe('StocksCalendarSummaryScreen', () => {
  it('should show an information banner if the offer is not disabled', () => {
    renderWithProviders(
      <StocksCalendarSummaryScreen
        offer={getIndividualOfferFactory({ status: OfferStatus.ACTIVE })}
      />
    )

    expect(
      screen.getByRole('link', {
        name: 'Nouvelle fenêtre Comment reporter ou annuler un évènement ?',
      })
    )
  })
})

import { OfferStatus } from 'apiClient/v1'
import { screen } from '@testing-library/react'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { IndividualOfferSummaryStocksCalendarScreen } from './IndividualOfferSummaryStocksCalendarScreen'

describe('IndividualOfferSummaryStocksCalendarScreen', () => {
  it('should show an information banner if the offer is not disabled', () => {
    renderWithProviders(
      <IndividualOfferSummaryStocksCalendarScreen
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

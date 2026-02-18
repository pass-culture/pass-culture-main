import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferSummaryStocksCalendarScreen } from './IndividualOfferSummaryStocksCalendarScreen'

describe('IndividualOfferSummaryStocksCalendarScreen', () => {
  it('should show an information banner if the offer is not disabled', async () => {
    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({ totalStockCount: 0, stocks: [] })
    )

    renderWithProviders(
      <IndividualOfferSummaryStocksCalendarScreen
        offer={getIndividualOfferFactory({ status: OfferStatus.ACTIVE })}
      />
    )

    expect(
      await screen.findByRole('link', {
        name: /Comment reporter ou annuler un évènement ?/,
      })
    ).toBeInTheDocument()
  })
})

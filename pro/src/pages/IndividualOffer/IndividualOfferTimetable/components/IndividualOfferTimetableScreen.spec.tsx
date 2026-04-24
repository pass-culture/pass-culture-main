import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualOfferTimetableScreen,
  type IndividualOfferTimetableScreenProps,
} from './IndividualOfferTimetableScreen'

const defaultProps: IndividualOfferTimetableScreenProps = {
  mode: OFFER_WIZARD_MODE.CREATION,
  offer: getIndividualOfferFactory(),
}

function renderIndividualOfferTimetableScreen(
  props?: Partial<IndividualOfferTimetableScreenProps>,
  features?: string[]
) {
  return renderWithProviders(
    <IndividualOfferTimetableScreen {...defaultProps} {...props} />,
    { features: features }
  )
}

describe('IndividualOfferTimetableScreen', () => {
  it('should render the stocks calendar', async () => {
    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({ totalStockCount: 0, stocks: [] })
    )

    renderIndividualOfferTimetableScreen({
      offer: getIndividualOfferFactory({ isEvent: true, hasStocks: false }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Horaires' })
    ).toBeInTheDocument()
  })
})

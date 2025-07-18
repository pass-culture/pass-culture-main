import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { IndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  getOfferStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { IndividualOfferSummaryStocksScreen } from './IndividualOfferSummaryStocksScreen'

const render = (offer: GetIndividualOfferWithAddressResponseModel) => {
  const contextValue = individualOfferContextValuesFactory({ offer })

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferSummaryStocksScreen />
    </IndividualOfferContext.Provider>
  )
}

const offer = getIndividualOfferFactory({ name: 'Offre de test' })

describe('IndividualOfferSummaryStocksScreen', () => {
  beforeEach(() => {
    vi.mock('apiClient/api', () => ({
      api: {
        getStocks: vi.fn(),
      },
    }))
  })

  it('should render a list of events', async () => {
    vi.spyOn(api, 'getStocks').mockResolvedValue({
      stocks: [
        getOfferStockFactory({ id: 1337, beginningDatetime: '2023-01-01' }),
        getOfferStockFactory({ id: 1338, beginningDatetime: '2023-01-02' }),
        getOfferStockFactory({ id: 1339, beginningDatetime: '2023-01-03' }),
      ],
      hasStocks: true,
      stockCount: 3,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('row', { name: /dim 01\/01\/2023 01:00 15\/09\/2021/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('row', { name: /lun 02\/01\/2023 01:00 15\/09\/2021/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('row', { name: /mar 03\/01\/2023 01:00 15\/09\/2021/ })
    ).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'

import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'commons/utils/factories/individualApiFactories'

import {
  StocksCalendarTable,
  StocksCalendarTableProps,
} from './StocksCalendarTable'

function renderStocksCalendarTable(
  props: Partial<StocksCalendarTableProps> = {}
) {
  render(
    <StocksCalendarTable
      departmentCode="56"
      checkedStocks={new Set()}
      offer={getIndividualOfferFactory()}
      onDeleteStocks={vi.fn()}
      updateCheckedStocks={vi.fn()}
      stocks={[
        getOfferStockFactory({ id: 1 }),
        getOfferStockFactory({ id: 2 }),
      ]}
      mode={OFFER_WIZARD_MODE.CREATION}
      {...props}
    />
  )
}

describe('StocksCalendarTable', () => {
  it('should show a placeholder message when there is no stock displayed in the table', () => {
    renderStocksCalendarTable({ stocks: [] })

    expect(screen.getByText('Aucune date trouvée')).toBeInTheDocument()
  })

  it('should not render stocks checkboxes options when the page is read only', () => {
    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.READ_ONLY })

    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  it('should not render stocks deletion options when the page is read only', () => {
    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.READ_ONLY })

    expect(
      screen.queryByRole('button', { name: 'Supprimer le stock' })
    ).not.toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'

import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'

import { StocksCalendarTable } from './StocksCalendarTable'

describe('StocksCalendarTable', () => {
  it('should show a placeholder message when there is no stock displayed in the table', () => {
    render(
      <StocksCalendarTable
        departmentCode="56"
        checkedStocks={new Set()}
        offer={getIndividualOfferFactory()}
        onDeleteStocks={vi.fn()}
        updateCheckedStocks={vi.fn()}
        stocks={[]}
      />
    )

    expect(screen.getByText('Aucune date trouvée')).toBeInTheDocument()
  })
})

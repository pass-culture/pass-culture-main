import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, subDays } from 'date-fns'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  StocksCalendarTable,
  StocksCalendarTableProps,
} from './StocksCalendarTable'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

function renderStocksCalendarTable(
  props: Partial<StocksCalendarTableProps> = {}
) {
  renderWithProviders(
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
      onUpdateStock={() => new Promise(() => {})}
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
      screen.queryByRole('button', { name: 'Supprimer la date' })
    ).not.toBeInTheDocument()
  })

  it('should not render the delete options when the stocks cannot be deleted', () => {
    renderStocksCalendarTable({
      stocks: [getOfferStockFactory({ id: 1, isEventDeletable: false })],
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer la date' })
    ).not.toBeInTheDocument()
  })

  it('should not render the delete and edit options when the offer is disabled (because it is rejected)', () => {
    renderStocksCalendarTable({
      offer: getIndividualOfferFactory({ status: OfferStatus.REJECTED }),
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer la date' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('should not render the delete and edit options when the offer is disabled (because it is pending)', () => {
    renderStocksCalendarTable({
      offer: getIndividualOfferFactory({ status: OfferStatus.PENDING }),
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer la date' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('should not render the edition options when the stocks beginning date is already passed', () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: subDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('should open the stock edition dialog when clicking on the edition action', async () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    expect(
      screen.getByRole('heading', { name: 'Modifier la date' })
    ).toBeInTheDocument()
  })

  it('should re-focus the edition action button when closing the dialog', async () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(
      screen.queryByRole('heading', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toHaveFocus()
  })
})

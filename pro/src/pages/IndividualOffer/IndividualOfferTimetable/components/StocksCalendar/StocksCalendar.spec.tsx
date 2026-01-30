import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from '@/apiClient/api'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { StocksCalendar, type StocksCalendarProps } from './StocksCalendar'

vi.mock('@/apiClient/api', () => ({
  api: {
    getStocks: vi.fn(),
    deleteStocks: vi.fn(),
    bulkCreateEventStocks: vi.fn(),
    bulkUpdateEventStocks: vi.fn(),
  },
}))

const defaultStocks = Array(19)
  .fill(null)
  .map((_, index) => getOfferStockFactory({ id: index }))

function renderStocksCalendar(
  stocks = defaultStocks,
  props?: Partial<StocksCalendarProps>
) {
  vi.spyOn(api, 'getStocks').mockResolvedValueOnce(
    getStocksResponseFactory({
      stocks,
      totalStockCount: stocks.length,
    })
  )

  renderWithProviders(
    <>
      <StocksCalendar
        offer={getIndividualOfferFactory({
          priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        })}
        mode={OFFER_WIZARD_MODE.CREATION}
        timetableTypeRadioGroupShown={false}
        {...props}
      />
      <SnackBarContainer />
    </>
  )
}

const LABEL = {
  addMore: 'Ajouter une ou plusieurs dates',
  emptyCta: 'Définir le calendrier',
}

describe('StocksCalendar', () => {
  it('shows empty state CTA when there are no stocks', () => {
    renderStocksCalendar([])

    expect(
      screen.getByRole('button', { name: LABEL.emptyCta })
    ).toBeInTheDocument()
  })

  it('opens the recurrence drawer from empty state CTA', async () => {
    renderStocksCalendar([])

    await userEvent.click(screen.getByRole('button', { name: LABEL.emptyCta }))

    expect(
      screen.getByRole('heading', { name: LABEL.emptyCta })
    ).toBeInTheDocument()
  })

  it('shows "add more" button when stocks exist and offer is not synchronized', () => {
    renderStocksCalendar()

    expect(
      screen.getByRole('button', { name: LABEL.addMore })
    ).toBeInTheDocument()
  })

  it('does not show "add more" button when offer is synchronized', () => {
    renderStocksCalendar(defaultStocks, {
      offer: getIndividualOfferFactory({ lastProvider: { name: '123' } }),
    })

    expect(
      screen.queryByRole('button', { name: LABEL.addMore })
    ).not.toBeInTheDocument()
  })

  it('navigates through pages', async () => {
    renderStocksCalendar(
      Array(50)
        .fill(null)
        .map((_, index) => getOfferStockFactory({ id: index }))
    )

    expect(
      screen.getByRole('button', { name: /Page 1 sur 3/ })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /page suivante/ }))
    expect(
      screen.getByRole('button', { name: /Page 2 sur 3/ })
    ).toBeInTheDocument()
  })

  it('goes back to page 1 when resetting filters', async () => {
    renderStocksCalendar(
      Array(50)
        .fill(null)
        .map((_, index) =>
          getOfferStockFactory({ id: index, priceCategoryId: 1 })
        )
    )

    await userEvent.click(screen.getByRole('button', { name: /page suivante/ }))
    expect(
      screen.getByRole('button', { name: /Page 2 sur 3/ })
    ).toBeInTheDocument()

    await userEvent.type(screen.getByLabelText('Horaire'), '00:00')
    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(
      screen.getByRole('button', { name: /Page 1 sur 3/ })
    ).toBeInTheDocument()
  })

  it('updates a stock (edition mode)', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
        editedStockCount: 1,
      })
    )

    renderStocksCalendar(
      [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      { mode: OFFER_WIZARD_MODE.EDITION }
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(api.bulkUpdateEventStocks).toHaveBeenCalled()
  })

  it('shows an error when none of the stocks were updated', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
        editedStockCount: 0,
      })
    )

    renderStocksCalendar(
      [
        getOfferStockFactory({
          id: 0,
          priceCategoryId: 0,
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      {
        offer: getIndividualOfferFactory({
          priceCategories: [
            { id: 0, label: 'Tarif 1', price: 1 },
            { id: 1, label: 'Tarif 2', price: 1 },
          ],
        }),
        mode: OFFER_WIZARD_MODE.EDITION,
      }
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )
    await userEvent.type(screen.getAllByLabelText(/Tarif/)[1], '1')
    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.getByText('Aucune date n’a pu être modifiée')
    ).toBeInTheDocument()
  })
})

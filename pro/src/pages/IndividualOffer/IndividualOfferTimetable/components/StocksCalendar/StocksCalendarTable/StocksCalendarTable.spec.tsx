import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, addSeconds, subDays, subSeconds } from 'date-fns'

import { OfferStatus, VenueState } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  StocksCalendarTable,
  type StocksCalendarTableProps,
} from './StocksCalendarTable'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

vi.mock('./StocksCalendarTableEditStock/StocksCalendarTableEditStock', () => ({
  StocksCalendarTableEditStock: ({ stock, onUpdateStock }: any) => (
    <div>
      <button
        onClick={() => {
          onUpdateStock({
            id: stock.id,
            beginningDatetime: addSeconds(
              new Date(stock.beginningDatetime),
              3600
            ).toISOString(),
            bookingLimitDatetime: stock.bookingLimitDatetime ?? null,
            priceCategoryId: stock.priceCategoryId ?? 1,
            quantity: stock.quantity ?? null,
          })
        }}
      >
        mock-update-time
      </button>
    </div>
  ),
}))

const defaultSelectedPartnerVenue = makeGetVenueResponseModel({ id: 1 })

function renderStocksCalendarTable(
  props: Partial<StocksCalendarTableProps> = {},
  isVenueClosed = false
) {
  const selectedPartnerVenue = isVenueClosed
    ? makeGetVenueResponseModel({ id: 1, state: VenueState.CLOSED })
    : defaultSelectedPartnerVenue

  return renderWithProviders(
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
      onUpdateFilters={vi.fn()}
      hasNoStocks={false}
      isLoading={false}
      pagination={{ pageCount: 1, currentPage: 1, onPageClick: vi.fn() }}
    />,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue,
        },
      },
    }
  )
}

describe('StocksCalendarTable', () => {
  it('should show a placeholder message when there is no stock displayed in the table', () => {
    renderStocksCalendarTable({ stocks: [] })

    expect(
      screen.getByText('Aucune date trouvée pour votre recherche')
    ).toBeInTheDocument()
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

  it('should not render the edit options when the offer is synchronized', () => {
    renderStocksCalendarTable({
      offer: getIndividualOfferFactory({ lastProvider: { name: '123' } }),
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('should render the edit options when the offer is synchronized with allociné', () => {
    renderStocksCalendarTable({
      offer: getIndividualOfferFactory({
        lastProvider: { name: 'Allociné' },
      }),
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addDays(new Date(), 1).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toBeInTheDocument()
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

  it('should not render the delete and edit options when the venue is closed', () => {
    renderStocksCalendarTable(
      {
        stocks: [
          getOfferStockFactory({
            id: 1,
            beginningDatetime: addDays(new Date(), 2).toISOString(),
          }),
        ],
        mode: OFFER_WIZARD_MODE.EDITION,
      },
      true
    )

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
          beginningDatetime: subDays(new Date(), 2).toISOString(),
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
          beginningDatetime: addDays(new Date(), 2).toISOString(),
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
          beginningDatetime: addDays(new Date(), 2).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    )

    expect(
      screen.queryByRole('heading', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toHaveFocus()
  })

  it('should disable the edition of a stock if its date is earlier today', () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: subSeconds(new Date(), 1).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('should enable the edition of a stock if its date is later today', () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addSeconds(new Date(), 1).toISOString(),
          bookingsQuantity: 1,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toBeInTheDocument()
  })

  it('should open a delete warning dialog when the user clicks on the delete button', async () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addSeconds(new Date(), 1).toISOString(),
          bookingsQuantity: 1,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer la date' })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Supprimer la date et annuler les réservations existantes ?',
      })
    ).toBeInTheDocument()
  })

  it('should show an explicit warning message in the deletion dialog when the stock has bookings', async () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addSeconds(new Date(), 1).toISOString(),
          bookingsQuantity: 10,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer la date' })
    )

    expect(
      screen.getByText((_content, element) => {
        return (
          element?.textContent ===
          'Cette action entrainera automatiquement l’annulation des réservations en cours et validées pour cette date. L’ensemble des bénéficiaires concernés sera averti par email.'
        )
      })
    ).toBeInTheDocument()
  })

  it('should delete directly without modal when deleting a stock without bookings', async () => {
    const onDeleteStocks = vi.fn()

    renderStocksCalendarTable({
      onDeleteStocks,
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addSeconds(new Date(), 1).toISOString(),
          bookingsQuantity: 0,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer la date' })
    )

    expect(onDeleteStocks).toHaveBeenCalledWith([1])
    expect(
      screen.queryByRole('heading', {
        name: 'Supprimer la date et annuler les réservations existantes ?',
      })
    ).not.toBeInTheDocument()
  })

  it('should open an edition warning modal and update only after confirmation when stock has bookings', async () => {
    const onUpdateStock = vi.fn().mockResolvedValue(undefined)

    renderStocksCalendarTable({
      onUpdateStock,
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString(),
          bookingsQuantity: 2,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'mock-update-time' })
    )

    expect(onUpdateStock).not.toHaveBeenCalled()
    expect(
      screen.getByRole('heading', {
        name: "Modifier l'horaire des réservations existantes ?",
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Confirmer la modification' })
    )

    expect(onUpdateStock).toHaveBeenCalledTimes(1)
  })

  it('should update directly without warning modal when stock has no bookings', async () => {
    const onUpdateStock = vi.fn().mockResolvedValue(undefined)

    renderStocksCalendarTable({
      onUpdateStock,
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString(),
          bookingsQuantity: 0,
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'mock-update-time' })
    )

    expect(onUpdateStock).toHaveBeenCalledTimes(1)
    expect(
      screen.queryByRole('heading', {
        name: "Modifier l'horaire des réservations existantes ?",
      })
    ).not.toBeInTheDocument()
  })
})

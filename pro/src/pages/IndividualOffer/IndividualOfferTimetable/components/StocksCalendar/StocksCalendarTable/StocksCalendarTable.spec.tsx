import { cleanup, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, addSeconds, subDays, subSeconds } from 'date-fns'

import { OfferStatus } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
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

function renderStocksCalendarTable(
  props: Partial<StocksCalendarTableProps> = {}
) {
  const onDeleteStocks = props.onDeleteStocks ?? vi.fn()
  const onUpdateFilters = props.onUpdateFilters ?? vi.fn()
  const setSelectedStocksIds = props.setSelectedStocksIds ?? vi.fn()

  renderWithProviders(
    <StocksCalendarTable
      departmentCode="56"
      selectedStocksIds={props.selectedStocksIds ?? new Set()}
      offer={props.offer ?? getIndividualOfferFactory()}
      onDeleteStocks={onDeleteStocks}
      setSelectedStocksIds={setSelectedStocksIds}
      stocks={
        props.stocks ?? [
          getOfferStockFactory({ id: 1 }),
          getOfferStockFactory({ id: 2 }),
        ]
      }
      isLoading={props.isLoading ?? false}
      onUpdateStock={props.onUpdateStock ?? (async () => {})}
      mode={props.mode ?? OFFER_WIZARD_MODE.CREATION}
      onUpdateFilters={onUpdateFilters}
      hasNoStocks={props.hasNoStocks ?? false}
    />
  )

  return { onDeleteStocks, onUpdateFilters, setSelectedStocksIds }
}

describe('StocksCalendarTable', () => {
  const user = userEvent.setup()

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    vi.useRealTimers()
  })

  it('shows "Réservations" column only when mode is not CREATION', () => {
    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.CREATION })
    expect(screen.queryByText('Réservations')).not.toBeInTheDocument()

    cleanup()

    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.EDITION })
    expect(screen.getByText('Réservations')).toBeInTheDocument()
  })

  it('shows "Actions" column only when mode is not READ_ONLY', () => {
    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.READ_ONLY })
    expect(screen.queryByText('Actions')).not.toBeInTheDocument()

    cleanup()

    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.EDITION })
    expect(screen.getByText('Actions')).toBeInTheDocument()
  })

  it('shows edit button only when editable rules are met', () => {
    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      offer: getIndividualOfferFactory({}), // not disabled, not synchronized
      stocks: [
        getOfferStockFactory({
          id: 1,
          isEventDeletable: true,
          beginningDatetime: addDays(new Date(), 2).toISOString(),
        }),
      ],
    })

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toBeInTheDocument()

    cleanup()

    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: subDays(new Date(), 1).toISOString(),
        }),
      ],
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('shows delete button only when stock is deletable and offer not disabled', () => {
    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      offer: getIndividualOfferFactory({}),
      stocks: [getOfferStockFactory({ id: 1, isEventDeletable: true })],
    })

    expect(
      screen.getByRole('button', { name: 'Supprimer la date' })
    ).toBeInTheDocument()

    cleanup()

    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [getOfferStockFactory({ id: 1, isEventDeletable: false })],
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer la date' })
    ).not.toBeInTheDocument()
  })

  it('confirms deletion and calls onDeleteStocks([id])', async () => {
    const { onDeleteStocks } = renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [
        getOfferStockFactory({
          id: 42,
          isEventDeletable: true,
          beginningDatetime: addSeconds(new Date(), 10).toISOString(),
        }),
      ],
    })

    await user.click(screen.getByRole('button', { name: 'Supprimer la date' }))
    await user.click(
      screen.getByRole('button', { name: 'Confirmer la suppression' })
    )

    expect(onDeleteStocks).toHaveBeenCalledWith([42])
  })

  it('shows warning text when deleting a stock with bookings', async () => {
    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [
        getOfferStockFactory({
          id: 1,
          isEventDeletable: true,
          bookingsQuantity: 2,
          beginningDatetime: addSeconds(new Date(), 10).toISOString(),
        }),
      ],
    })

    await user.click(screen.getByRole('button', { name: 'Supprimer la date' }))

    expect(
      screen.getByText(/entraînera l’annulation des réservations/i)
    ).toBeInTheDocument()
  })

  it('triggers filter reset from no-result state', async () => {
    const { onUpdateFilters } = renderStocksCalendarTable({
      stocks: [],
      hasNoStocks: false,
    })

    await user.click(
      screen.getByRole('button', { name: 'Afficher toutes les dates' })
    )

    expect(onUpdateFilters).toHaveBeenCalled()
  })

  it('shows no-result placeholder when stocks are empty and hasNoStocks is false', () => {
    renderStocksCalendarTable({ stocks: [], hasNoStocks: false })

    expect(
      screen.getByText('Aucune date trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('shows no-data block when hasNoStocks is true', () => {
    renderStocksCalendarTable({ stocks: [], hasNoStocks: true })

    expect(
      screen.getByText('Vous n’avez pas encore de dates')
    ).toBeInTheDocument()
  })

  it('does not render checkboxes when mode is READ_ONLY', () => {
    renderStocksCalendarTable({ mode: OFFER_WIZARD_MODE.READ_ONLY })
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  it('does not render delete/edit options when offer is disabled (REJECTED)', () => {
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

  it('does not render edit option when offer is synchronized (non allociné)', () => {
    renderStocksCalendarTable({
      offer: getIndividualOfferFactory({ lastProvider: { name: '123' } }),
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addDays(new Date(), 1).toISOString(),
        }),
      ],
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()
  })

  it('renders edit option when offer is synchronized with Allociné', () => {
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

  it('does not render edit option when the stock beginning date is already passed', () => {
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

  it('opens the edit dialog when clicking on edit action', async () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addDays(new Date(), 2).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await user.click(screen.getByRole('button', { name: 'Modifier la date' }))

    expect(
      screen.getByRole('heading', { name: 'Modifier la date' })
    ).toBeInTheDocument()
  })

  it('re-focuses the edit action button when closing the dialog', async () => {
    vi.useFakeTimers()

    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    const editButton = screen.getByRole('button', { name: 'Modifier la date' })
    // or: const editButton = screen.getByTitle('Modifier la date')

    await user.click(editButton)

    await user.click(screen.getByRole('button', { name: 'Annuler' }))

    vi.runAllTimers()

    expect(
      screen.queryByRole('heading', { name: 'Modifier la date' })
    ).not.toBeInTheDocument()

    expect(editButton).toHaveFocus()
  })

  it('disables edition if date is earlier today', () => {
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

  it('enables edition if date is later today', () => {
    renderStocksCalendarTable({
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addSeconds(new Date(), 1).toISOString(),
        }),
      ],
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    expect(
      screen.getByRole('button', { name: 'Modifier la date' })
    ).toBeInTheDocument()
  })

  it('does not show warning block in deletion dialog when stock has no bookings', async () => {
    renderStocksCalendarTable({
      mode: OFFER_WIZARD_MODE.EDITION,
      stocks: [
        getOfferStockFactory({
          beginningDatetime: addSeconds(new Date(), 10).toISOString(),
          bookingsQuantity: 0,
          isEventDeletable: true,
        }),
      ],
    })

    await user.click(screen.getByRole('button', { name: 'Supprimer la date' }))

    expect(
      screen.queryByText(/entraînera l’annulation des réservations/i)
    ).not.toBeInTheDocument()
  })
})

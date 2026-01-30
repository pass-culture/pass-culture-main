import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
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
      stocks: stocks,
      totalStockCount: stocks.length,
    })
  )

  vi.spyOn(api, 'bulkCreateEventStocks').mockResolvedValue(
    getStocksResponseFactory({
      stocks: stocks,
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
  noDateAction: 'Ajouter une ou plusieurs dates',
  dateAction: 'Définir le calendrier',
}

describe('StocksCalendar', () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should display a button to add calendar infos when there are no stocks yet', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', { name: LABEL.dateAction })
    ).toBeInTheDocument()
  })

  it('should display an info banner', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByText(
        /Les bénéficiaires peuvent annuler jusqu'à 48h avant l'événement/
      )
    ).toBeInTheDocument()
  })

  it('should not display an info banner if the offer is disabled', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        status: OfferStatus.REJECTED,
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByText(/Les bénéficiaires ont 48h pour annuler/)
    ).not.toBeInTheDocument()
  })

  it('should open the recurrence form when clicking on the button when there are no stocks yet', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.dateAction })
    )

    expect(
      screen.getByRole('heading', {
        name: LABEL.dateAction,
      })
    ).toBeInTheDocument()
  })

  it('should show a button to add more stocks if there are already stocks in the table', async () => {
    renderStocksCalendar()

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.noDateAction })
    )

    expect(
      screen.getByRole('heading', {
        name: LABEL.noDateAction,
      })
    ).toBeInTheDocument()
  })

  it('should delete a stock from the stock line trash button', async () => {
    renderStocksCalendar()

    const deleteSpy = vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
      })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer la date' })[0]
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Confirmer la suppression' })
    )

    expect(deleteSpy).toHaveBeenCalledOnce()

    expect(screen.getByText(/Une date a été supprimée/)).toBeInTheDocument()
  })

  it('should delete all the checked stocks', async () => {
    renderStocksCalendar()

    const deleteSpy = vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
      })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )
    await userEvent.click(screen.getAllByRole('checkbox')[2])
    await userEvent.click(screen.getAllByRole('checkbox')[2])

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ces dates' })
    )

    expect(deleteSpy).toHaveBeenCalledOnce()

    expect(screen.getByText(/19 dates ont été supprimées/)).toBeInTheDocument()
  })

  it('should close the dialog when the form is validated', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.dateAction })
    )

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText(/Horaire 1/), '22:22')

    await userEvent.selectOptions(screen.getByLabelText(/Tarif/), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.queryByRole('heading', {
        name: LABEL.dateAction,
      })
    ).not.toBeInTheDocument()
  })

  it('should navigate through the pages', async () => {
    renderStocksCalendar(
      Array(50)
        .fill(null)
        .map((_, index) => getOfferStockFactory({ id: index }))
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', { name: /Page 1 sur 3/ })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /page suivante/ }))

    expect(
      screen.getByRole('button', { name: /Page 2 sur 3/ })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /page précédente/ })
    )

    expect(
      screen.getByRole('button', { name: /Page 1 sur 3/ })
    ).toBeInTheDocument()
  })

  it('should show the total number of stocks', async () => {
    renderStocksCalendar(
      Array(50)
        .fill(null)
        .map((_, index) => getOfferStockFactory({ id: index }))
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.getByText('50 dates')).toBeInTheDocument()
  })

  it('should not show the total number of stocks if there is none', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.queryByText(/0 dates/)).not.toBeInTheDocument()
  })

  it('should update a specific stock', async () => {
    renderStocksCalendar(
      [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      {
        mode: OFFER_WIZARD_MODE.EDITION,
      }
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    const updateStockSpy = vi.spyOn(api, 'bulkUpdateEventStocks')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(updateStockSpy).toHaveBeenCalled()
  })

  it('should show an error message when the added stocks are in the past', async () => {
    Element.prototype.scrollIntoView = vi.fn()

    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif', price: 1 }],
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.dateAction })
    )

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      new Date().toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText(/Horaire 1/), '00:00')

    await userEvent.selectOptions(screen.getByLabelText(/Tarif/), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.getByText('L’évènement doit être à venir')
    ).toBeInTheDocument()
  })

  it('should go back to page 1 when filtering', async () => {
    renderStocksCalendar(
      Array(50)
        .fill(null)
        .map((_, index) =>
          getOfferStockFactory({ id: index, priceCategoryId: 1 })
        )
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

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

  it('should show an error message when none of the stocks were updated', async () => {
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

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.type(screen.getAllByLabelText(/Tarif/)[1], '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.getByText('Aucune date n’a pu être modifiée')
    ).toBeInTheDocument()
  })

  it('should not show a button to add more stocks if the offer is synchronized', async () => {
    renderStocksCalendar(defaultStocks, {
      offer: getIndividualOfferFactory({ lastProvider: { name: '123' } }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('button', { name: LABEL.noDateAction })
    ).not.toBeInTheDocument()
  })

  it('should show success message after deleting multiple stocks', async () => {
    const stocks = Array(5)
      .fill(null)
      .map((_, index) => getOfferStockFactory({ id: index }))

    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({
        stocks,
        totalStockCount: stocks.length,
      })
    )

    vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 2,
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
        />
        <SnackBarContainer />
      </>
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(screen.getAllByRole('checkbox')[1])
    await userEvent.click(screen.getAllByRole('checkbox')[2])
    await userEvent.click(screen.getAllByRole('checkbox')[3])

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ces dates' })
    )

    expect(screen.getByText(/3 dates ont été supprimées/)).toBeInTheDocument()
  })

  it('should delete stocks and refresh offer in edition mode', async () => {
    renderStocksCalendar(defaultStocks, {
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    const deleteSpy = vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
      })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer la date' })[0]
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Confirmer la suppression' })
    )

    expect(deleteSpy).toHaveBeenCalledOnce()

    expect(screen.getByText(/Une date a été supprimée/)).toBeInTheDocument()
  })

  it('should show an error message when updating a stock fails', async () => {
    renderStocksCalendar(
      [
        getOfferStockFactory({
          id: 1,
          beginningDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        }),
      ],
      {
        mode: OFFER_WIZARD_MODE.EDITION,
      }
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    vi.spyOn(api, 'bulkUpdateEventStocks').mockRejectedValueOnce(
      new Error('Network error')
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    await waitFor(() => {
      expect(
        screen.getByText(
          'Une erreur est survenue lors de la modification des dates'
        )
      ).toBeInTheDocument()
    })
  })

  it('should update sorting when selecting a sort option', async () => {
    const stocksResponse = getStocksResponseFactory({
      stocks: defaultStocks,
      totalStockCount: defaultStocks.length,
    })

    const getStocksSpy = vi
      .spyOn(api, 'getStocks')
      .mockResolvedValueOnce(stocksResponse)
      .mockResolvedValueOnce(stocksResponse)

    renderWithProviders(
      <>
        <StocksCalendar
          offer={getIndividualOfferFactory({
            priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
          })}
          mode={OFFER_WIZARD_MODE.CREATION}
          timetableTypeRadioGroupShown={false}
        />
        <SnackBarContainer />
      </>
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.selectOptions(
      screen.getByLabelText('Trier par'),
      'REMAINING_QUANTITY desc'
    )

    await waitFor(() => {
      expect(getStocksSpy).toHaveBeenLastCalledWith(
        expect.anything(),
        undefined,
        undefined,
        undefined,
        'REMAINING_QUANTITY',
        true,
        1,
        20
      )
    })
  })

  it('should display "Aucune date à afficher" for synchronized offers without stocks', async () => {
    renderStocksCalendar([], {
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Tarif 1', price: 1 }],
        lastProvider: { name: 'Provider' },
        hasStocks: false,
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.getByText('Aucune date à afficher')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: LABEL.dateAction })
    ).not.toBeInTheDocument()
  })

  it('should not show header section in read only mode', async () => {
    renderStocksCalendar(defaultStocks, {
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('heading', { name: 'Horaires' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: LABEL.noDateAction })
    ).not.toBeInTheDocument()
  })

  it('should show subtitle when timetableTypeRadioGroupShown is true', async () => {
    renderStocksCalendar(defaultStocks, {
      timetableTypeRadioGroupShown: true,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    const heading = screen.getByRole('heading', { name: 'Horaires' })
    expect(heading.tagName).toBe('H3')
  })
})

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from '@/apiClient/api'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { StocksCalendar, StocksCalendarProps } from './StocksCalendar'

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
  vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
    stocks: stocks,
    stockCount: stocks.length,
    hasStocks: stocks.length > 0,
  })

  vi.spyOn(api, 'bulkCreateEventStocks').mockResolvedValue({ stocks_count: 20 })

  renderWithProviders(
    <>
      <StocksCalendar
        offer={getIndividualOfferFactory()}
        mode={OFFER_WIZARD_MODE.CREATION}
        {...props}
      />
      <Notification />
    </>
  )
}

describe('StocksCalendar', () => {
  it('should display a button to add calendar infos when there are no stocks yet', async () => {
    renderStocksCalendar([])

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    ).toBeInTheDocument()
  })

  it('should open the recurrence form when clicking on the button when there are no stocks yet', async () => {
    renderStocksCalendar([])

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Définir le calendrier de votre offre',
      })
    ).toBeInTheDocument()
  })

  it('should show a button to add more stocks if there are already stocks in the table', async () => {
    renderStocksCalendar()

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter une ou plusieurs dates' })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Définir le calendrier de votre offre',
      })
    ).toBeInTheDocument()
  })

  it('should delete a stock from the stock line trash button', async () => {
    renderStocksCalendar()

    const deleteSpy = vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce()

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

    const deleteSpy = vi.spyOn(api, 'deleteStocks').mockResolvedValueOnce()

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
    renderStocksCalendar([])

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    )

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '22:22')

    await userEvent.selectOptions(screen.getByLabelText('Tarif *'), '6')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.queryByRole('heading', {
        name: 'Définir le calendrier de votre offre',
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

    expect(screen.getByText('Page 1/3'))

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))

    expect(screen.getByText('Page 2/3'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )

    expect(screen.getByText('Page 1/3'))
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
    renderStocksCalendar([])

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.queryByText(/ dates/)).not.toBeInTheDocument()
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
      }),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    )

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      new Date().toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '00:00')

    await userEvent.selectOptions(screen.getByLabelText('Tarif *'), '1')

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

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))

    expect(screen.getByText('Page 2/3'))

    await userEvent.type(screen.getByLabelText('Horaire'), '00:00')

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(screen.getByText('Page 1/3'))
  })

  it('should show an error message when none of the stocks were updated', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValueOnce({
      stocks_count: 0,
    })

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

    await userEvent.type(screen.getByLabelText('Tarif *'), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.getByText('Aucune date n’a pu être modifiée')
    ).toBeInTheDocument()
  })
})

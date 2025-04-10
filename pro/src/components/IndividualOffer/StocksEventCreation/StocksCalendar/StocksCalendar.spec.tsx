import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from 'apiClient/api'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import { StocksCalendar } from './StocksCalendar'

vi.mock('apiClient/api', () => ({
  api: {
    getStocks: vi.fn(),
    deleteStocks: vi.fn(),
    upsertStocks: vi.fn(),
  },
}))

const defaultStocks = Array(19)
  .fill(null)
  .map((_, index) => getOfferStockFactory({ id: index }))

function renderStocksCalendar(stocks = defaultStocks) {
  vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
    stocks: stocks,
    stockCount: stocks.length,
    hasStocks: stocks.length > 0,
  })

  vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks_count: 20 })

  renderWithProviders(
    <>
      <StocksCalendar
        offer={getIndividualOfferFactory()}
        handleNextStep={() => {}}
        handlePreviousStep={() => {}}
        departmentCode="56"
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
      screen.getAllByRole('button', { name: 'Supprimer le stock' })[0]
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
      screen.getByRole('checkbox', { name: 'Sélectionner tous les stocks' })
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
      screen.getByLabelText('Date *'),
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
})

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { StocksCalendar } from './StocksCalendar'

function renderStocksCalendar() {
  renderWithProviders(<StocksCalendar offer={getIndividualOfferFactory()} />)
}

describe('StocksCalendar', () => {
  it('should display a button to add calendar infos', () => {
    renderStocksCalendar()

    expect(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    ).toBeInTheDocument()
  })

  it('should open the recurrence form when clicking on the button', async () => {
    renderStocksCalendar()

    await userEvent.click(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Définir le calendrier de votre offre',
      })
    ).toBeInTheDocument()
  })
})

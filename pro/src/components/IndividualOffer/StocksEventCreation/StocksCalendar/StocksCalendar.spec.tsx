import { render, screen } from '@testing-library/react'

import { StocksCalendar } from './StocksCalendar'

describe('StocksCalendar', () => {
  it('should display a button to add calendar infos', () => {
    render(<StocksCalendar />)

    expect(
      screen.getByRole('button', { name: 'Définir le calendrier' })
    ).toBeInTheDocument()
  })
})

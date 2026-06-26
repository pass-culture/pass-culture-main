import { render, screen } from '@testing-library/react'

import { OpeningHoursReadOnly } from '../OpeningHoursReadOnly'

describe('OpeningHours', () => {
  it('should display the closed-all-days message when there are no opening hours', () => {
    render(<OpeningHoursReadOnly openingHours={null} />)

    expect(screen.getByText(/fermé tous les jours/)).toBeInTheDocument()
  })

  it('should display the closed-all-days message when every day is empty', () => {
    render(<OpeningHoursReadOnly openingHours={{ MONDAY: [], SUNDAY: null }} />)

    expect(screen.getByText(/fermé tous les jours/)).toBeInTheDocument()
  })

  it('should only list the days that have opening hours, in order', () => {
    const { container } = render(
      <OpeningHoursReadOnly
        openingHours={{
          MONDAY: [['09:00', '12:00']],
          WEDNESDAY: [
            ['10:00', '13:00'],
            ['14:00', '19:00'],
          ],
          SUNDAY: null,
        }}
      />
    )

    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
    expect(screen.getByText(/Mercredi/)).toBeInTheDocument()
    expect(container).toHaveTextContent('09:00-12:00')
    expect(container).toHaveTextContent('10:00-13:00 et 14:00-19:00')

    expect(screen.queryByText(/Dimanche/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Mardi/)).not.toBeInTheDocument()
  })
})

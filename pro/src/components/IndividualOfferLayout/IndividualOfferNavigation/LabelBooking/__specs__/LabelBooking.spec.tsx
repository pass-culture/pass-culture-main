import { render, screen } from '@testing-library/react'

import { LabelBooking } from '../LabelBooking'

describe('LabelBooking', () => {
  it('should render stepper in creation', () => {
    render(<LabelBooking bookingsCount={123} />)

    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('123')).toBeInTheDocument()
  })

  it('should not display 0', () => {
    render(<LabelBooking bookingsCount={0} />)

    expect(screen.queryByText(/0/)).not.toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'

import { LabelBooking } from '../LabelBooking'

describe('LabelBooking', () => {
  it('should render stepper in creation', () => {
    render(<LabelBooking bookingsCount={123} />)

    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('123')).toBeInTheDocument()
  })
})

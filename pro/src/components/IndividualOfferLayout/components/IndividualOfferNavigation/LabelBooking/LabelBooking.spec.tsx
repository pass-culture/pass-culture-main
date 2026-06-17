import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { LabelBooking } from './LabelBooking'

describe('LabelBooking', () => {
  it('should render stepper in creation', () => {
    renderWithProviders(<LabelBooking bookingsCount={123} />)

    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('123')).toBeInTheDocument()
  })

  it('should not display 0', () => {
    renderWithProviders(<LabelBooking bookingsCount={0} />)

    expect(screen.queryByText(/0/)).not.toBeInTheDocument()
  })

  it('should not display bookings count when WIP_OFFER_EXPOSURE is enabled', () => {
    renderWithProviders(<LabelBooking bookingsCount={123} />, {
      features: ['WIP_OFFER_EXPOSURE'],
    })
    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.queryByText('123')).not.toBeInTheDocument()
  })
})

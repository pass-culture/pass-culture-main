import { render, screen } from '@testing-library/react'

import { Header, HeaderProps } from '../Header'

const renderHeader = (props: HeaderProps) => render(<Header {...props} />)

const defaultProps: HeaderProps = {
  bookingsRecapFilteredLength: 1,
  isLoading: false,
  resetBookings: vi.fn(),
}

describe("bookings recap table's header", () => {
  it('should display the appropriate message when there is one booking', () => {
    // When
    renderHeader(defaultProps)

    // Then
    expect(screen.queryByText('1 réservation')).toBeInTheDocument()
  })

  it('should display the appropriate message when there is several booking', () => {
    // Given
    const props = {
      ...defaultProps,
      bookingsRecapFilteredLength: 2,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('2 réservations')).toBeInTheDocument()
  })

  it('should only display a specific message when data are still loading', () => {
    // Given
    const props = {
      ...defaultProps,
      bookingsRecapFilteredLength: 0,
      isLoading: true,
    }

    // When
    renderHeader(props)

    // Then
    expect(
      screen.getByText('Chargement des réservations...')
    ).toBeInTheDocument()
  })

  it('should display show all booking button when default booking id provided', () => {
    // Given
    const props = { ...defaultProps, queryBookingId: '1' }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('1 réservation')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Voir toutes les réservations' })
    ).toBeInTheDocument()
  })
})

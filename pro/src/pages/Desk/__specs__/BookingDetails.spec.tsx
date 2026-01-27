import { screen } from '@testing-library/react'

import * as useIsCaledonian from '@/commons/hooks/useIsCaledonian'
import * as convertEuroToPacificFranc from '@/commons/utils/convertEuroToPacificFranc'
import { defaultGetBookingResponse } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { BookingDetails, type BookingDetailsProps } from '../BookingDetails'

function renderBookingDetails({ booking }: BookingDetailsProps) {
  renderWithProviders(<BookingDetails booking={booking} />)
}

describe('BookingDetails', () => {
  it('should display duo booking when the booking is for two people', () => {
    renderBookingDetails({
      booking: { ...defaultGetBookingResponse, quantity: 2 },
    })

    expect(
      screen.getByRole('img', { name: 'Réservation DUO' })
    ).toBeInTheDocument()
  })

  it('should format the booking date when the booking has a starting date', () => {
    renderBookingDetails({
      booking: {
        ...defaultGetBookingResponse,
        datetime: '2001-02-01T20:00:00Z',
      },
    })

    expect(screen.getByText('01/02/2001 - 21h00')).toBeInTheDocument()
  })

  it("should format the booking date as 'Permanent' when the booking doesn't have a starting date", () => {
    renderBookingDetails({
      booking: { ...defaultGetBookingResponse, datetime: '' },
    })

    expect(screen.getByText('Permanent')).toBeInTheDocument()
  })

  it('should format the booking date even when the department code of the venue is not defined', () => {
    renderBookingDetails({
      booking: {
        ...defaultGetBookingResponse,
        offerDepartmentCode: null,
      },
    })

    expect(screen.getByText('01/02/2001 - 21h00')).toBeInTheDocument()
  })

  it('should display price in CFP for caledonian user (quantity 1)', () => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValue(true)
    vi.spyOn(
      convertEuroToPacificFranc,
      'convertEuroToPacificFranc'
    ).mockImplementation(() => 1234)

    renderBookingDetails({
      booking: { ...defaultGetBookingResponse, price: 10, quantity: 1 },
    })

    expect(screen.getByText('1 234 F')).toBeInTheDocument()
  })

  it('should display price in CFP for caledonian user (quantity 2)', () => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValue(true)
    vi.spyOn(
      convertEuroToPacificFranc,
      'convertEuroToPacificFranc'
    ).mockImplementation(() => 2468)

    renderBookingDetails({
      booking: { ...defaultGetBookingResponse, price: 10, quantity: 2 },
    })

    expect(screen.getByText('2 468 F')).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: 'Réservation DUO' })
    ).toBeInTheDocument()
  })
})

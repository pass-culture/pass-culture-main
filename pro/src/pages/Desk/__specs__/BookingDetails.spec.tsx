import { render, screen } from '@testing-library/react'

import { defaultGetBookingResponse } from '@/commons/utils/factories/individualApiFactories'

import { BookingDetails } from '../BookingDetails'

describe('BookingDetails', () => {
  it('should display duo booking when the booking is for two people', () => {
    render(
      <BookingDetails
        {...{
          booking: { ...defaultGetBookingResponse, quantity: 2 },
        }}
      />
    )

    expect(screen.getByRole('img', { name: 'Réservation DUO' }))
  })

  it('should format the booking date when the booking has a starting date', () => {
    render(
      <BookingDetails
        {...{
          booking: {
            ...defaultGetBookingResponse,
            datetime: '2001-02-01T20:00:00Z',
          },
        }}
      />
    )

    expect(screen.getByText('01/02/2001 - 21h00'))
  })

  it("should format the booking date as 'Permanent' when the booking doesn't have a starting date", () => {
    render(
      <BookingDetails
        {...{
          booking: { ...defaultGetBookingResponse, datetime: '' },
        }}
      />
    )

    expect(screen.getByText('Permanent'))
  })

  it('should format the booking date even when the department code of the venue is not defined', () => {
    render(
      <BookingDetails
        {...{
          booking: {
            ...defaultGetBookingResponse,
            offerDepartmentCode: undefined,
          },
        }}
      />
    )

    expect(screen.getByText('01/02/2001 - 21h00'))
  })
})

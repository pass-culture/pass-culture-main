import findOldestBookingDate from '../findOldestBookingDate'
import { EMPTY_FILTER_VALUE } from '../../Filters/_constants'

describe('findOldestBookingDate', () => {
  it('should return null when bookings list is empty', () => {
    // given
    const bookingsRecap = []

    // when
    const result = findOldestBookingDate(bookingsRecap)

    // then
    expect(result).toBe(EMPTY_FILTER_VALUE)
  })

  it('should return the oldest date', () => {
    // given
    const bookingsRecap = [
      {
        stock: {
          offer_name: 'Merlin enchanteur',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
      },
      {
        stock: {
          offer_name: 'Jurrasic Perk',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-01-12T12:00:00Z',
        booking_token: 'ZACBGD',
        booking_status: 'Validé',
      },
    ]

    // when
    const result = findOldestBookingDate(bookingsRecap)

    // then
    expect(result).toStrictEqual('2020-01-12T12:00:00Z')
  })
})

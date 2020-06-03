import generateBookingsCsvFile, { CSV_HEADERS } from '../generateBookingsCsvFile'

describe('generateBookingsCsvFile', () => {
  it('should return data with csv header', () => {
    // given
    const bookings = []

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([CSV_HEADERS])
  })

  it('should return data with all bookings', () => {
    // given
    const bookings = [
      {
        stock: {
          event_beginning_datetime: '2020-05-12T11:03:28+04:00',
          offer_name: 'Avez-vous déjà vu',
          type: 'event',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00+02:00',
        booking_token: 'ZEHBGD',
        booking_status: 'validated',
        booking_is_duo: false,
        venue_identifier: 'AE'
      },
      {
        stock: {
          offer_name: 'Jurassic Park',
          type: 'thing',
        },
        beneficiary: {
          lastname: 'LaMerguez',
          firstname: 'Daniel',
          email: 'daniel.lamerguez@example.com',
        },
        booking_date: '2020-05-01T14:12:00Z',
        booking_token: 'ABCDEF',
        booking_status: 'cancelled',
        booking_is_duo: false,
        venue_identifier: 'AE'
      }
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      ['Avez-vous déjà vu', '12/05/2020 11:03', 'Klepi Sonia', 'sonia.klepi@example.com', '03/04/2020 12:00', 'ZEHBGD', 'validé'],
      ['Jurassic Park', '', 'LaMerguez Daniel', 'daniel.lamerguez@example.com', '01/05/2020 14:12', 'ABCDEF', 'annulé'],
    ])
  })
})

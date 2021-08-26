/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

import generateBookingsCsvFile, { CSV_HEADERS } from '../generateBookingsCsvFile'

describe('generateBookingsCsvFile', () => {
  let validated_booking
  let canceled_booking

  beforeEach(() => {
    validated_booking = {
      stock: {
        event_beginning_datetime: '2021-06-09T11:03:28+05:00',
        offer_name: 'Avez-vous déjà vu',
        type: 'event',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
        phonenumber: '0100000000',
      },
      booking_date: '2021-06-09T16:15:12.219158+02:00',
      booking_token: 'ZEHBGD',
      booking_status: 'validated',
      booking_status_history: [
        {
          date: '2021-06-09T16:15:12.219158+02:00',
          status: 'booked',
        },
        {
          date: '2021-06-09T16:30:35.332610+02:00',
          status: 'validated',
        },
      ],
      booking_is_duo: false,
      booking_amount: 1.6,
      offerer: {
        name: 'Le conseil des FNAC',
      },
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber',
      },
    }

    canceled_booking = {
      stock: {
        offer_name: 'Jurassic Park',
        type: 'thing',
      },
      beneficiary: {
        lastname: 'LaMerguez',
        firstname: 'Daniel',
        email: 'daniel.lamerguez@example.com',
        phonenumber: '0100000000',
      },
      booking_date: '2020-05-01T14:12:00Z',
      booking_token: 'ABCDEF',
      booking_status: 'cancelled',
      booking_status_history: [
        {
          date: '2020-05-01T14:12:00Z',
          status: 'booked',
        },
        {
          date: '2020-05-01T16:12:00Z',
          status: 'canceled',
        },
      ],
      booking_is_duo: false,
      booking_amount: 5.4,
      offerer: {
        name: 'Le conseil des FNAC',
      },
      venue: {
        identifier: 'AB',
        name: 'La FNAC Lyon',
      },
    }
  })

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
    const bookings = [validated_booking, canceled_booking]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'Librairie Kléber',
        'Avez-vous déjà vu',
        '09/06/2021 11:03',
        '',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '0100000000',
        '09/06/2021 16:15',
        '09/06/2021 16:30',
        'ZEHBGD',
        '1,6',
        'validé',
      ],
      [
        'La FNAC Lyon',
        'Jurassic Park',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '0100000000',
        '01/05/2020 14:12',
        '',
        'ABCDEF',
        '5,4',
        'annulé',
      ],
    ])
  })

  it('should add isbn only when stock has isbn value', () => {
    // given
    const bookings = [
      {
        ...validated_booking,
        stock: {
          offer_name: 'Avez-vous déjà vu',
          type: 'thing',
          offer_isbn: '9781234567654',
        },
      },
      canceled_booking,
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'Librairie Kléber',
        'Avez-vous déjà vu',
        '',
        '9781234567654',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '0100000000',
        '09/06/2021 16:15',
        '09/06/2021 16:30',
        'ZEHBGD',
        '1,6',
        'validé',
      ],
      [
        'La FNAC Lyon',
        'Jurassic Park',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '0100000000',
        '01/05/2020 14:12',
        '',
        'ABCDEF',
        '5,4',
        'annulé',
      ],
    ])
  })

  it('should escape offer name containing double quotes', () => {
    // given
    const bookings = [
      {
        ...validated_booking,
        stock: {
          offer_name: 'Avez-vous "déjà" "vu"',
          type: 'thing',
          offer_isbn: '9781234567654',
        },
      },
      {
        ...canceled_booking,
        stock: {
          offer_name: 'Jurassic "Park"',
          type: 'thing',
        },
      },
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'Librairie Kléber',
        'Avez-vous ""déjà"" ""vu""',
        '',
        '9781234567654',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '0100000000',
        '09/06/2021 16:15',
        '09/06/2021 16:30',
        'ZEHBGD',
        '1,6',
        'validé',
      ],
      [
        'La FNAC Lyon',
        'Jurassic ""Park""',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '0100000000',
        '01/05/2020 14:12',
        '',
        'ABCDEF',
        '5,4',
        'annulé',
      ],
    ])
  })

  it('should return data with all bookings using offerer name when venue is virtual', () => {
    // given
    const bookings = [
      {
        ...validated_booking,
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber',
          is_virtual: false,
        },
      },
      {
        ...canceled_booking,
        venue: {
          identifier: 'AB',
          name: 'La FNAC Lyon',
          is_virtual: true,
        },
      },
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'Librairie Kléber',
        'Avez-vous déjà vu',
        '09/06/2021 11:03',
        '',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '0100000000',
        '09/06/2021 16:15',
        '09/06/2021 16:30',
        'ZEHBGD',
        '1,6',
        'validé',
      ],
      [
        'Le conseil des FNAC - Offre numérique',
        'Jurassic Park',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '0100000000',
        '01/05/2020 14:12',
        '',
        'ABCDEF',
        '5,4',
        'annulé',
      ],
    ])
  })
})

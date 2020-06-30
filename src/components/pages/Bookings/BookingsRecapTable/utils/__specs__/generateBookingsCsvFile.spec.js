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
        booking_amount: 2,
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber'
        }
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
        booking_amount: 5,
        venue: {
          identifier: 'AB',
          name: 'La FNAC Lyon'
        }
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
        '12/05/2020 11:03',
        '',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '03/04/2020 12:00',
        'ZEHBGD',
        2,
        'validé',
      ],
      [
        'La FNAC Lyon',
        'Jurassic Park',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '01/05/2020 14:12',
        'ABCDEF',
        5,
        'annulé',
      ],
    ])
  })

  it('should add isbn only when stock has isbn value', () => {
    // given
    const bookings = [
      {
        stock: {
          offer_name: 'Avez-vous déjà vu',
          type: 'thing',
          offer_isbn: '9781234567654',
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
        booking_amount: 1,
        venue: {
          identifier: 'AB',
          name: 'La FNAC Lyon'
        }
      },
      {
        stock: {
          offer_name: 'Jurassic Park',
          type: 'thing',
        },
        beneficiary: {
          lastname: 'LaGuez',
          firstname: 'Anthony',
          email: 'anthony.laguez@example.com',
        },
        booking_date: '2020-05-01T14:12:00Z',
        booking_token: 'ABCDEF',
        booking_status: 'cancelled',
        booking_is_duo: false,
        booking_amount: 2,
        venue: {
          identifier: 'KF',
          name: 'Librairie Kléber'
        }
      },
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'La FNAC Lyon',
        'Avez-vous déjà vu',
        '',
        '9781234567654',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '03/04/2020 12:00',
        'ZEHBGD',
        1,
        'validé',
      ],
      [
        'Librairie Kléber',
        'Jurassic Park',
        '',
        '',
        'LaGuez Anthony',
        'anthony.laguez@example.com',
        '01/05/2020 14:12',
        'ABCDEF',
        2,
        'annulé',
      ],
    ])
  })

  it('should escape offer name containing double quotes', () => {
    // given
    const bookings = [
      {
        stock: {
          offer_name: 'Avez-vous "déjà" "vu"',
          type: 'thing',
          offer_isbn: '9781234567654',
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
        booking_amount: 1,
        venue: {
          identifier: 'AB',
          name: 'La FNAC Lyon'
        }
      },
      {
        stock: {
          offer_name: 'Jurassic "Park"',
          type: 'thing',
        },
        beneficiary: {
          lastname: 'LaGuez',
          firstname: 'Anthony',
          email: 'anthony.laguez@example.com',
        },
        booking_date: '2020-05-01T14:12:00Z',
        booking_token: 'ABCDEF',
        booking_status: 'cancelled',
        booking_is_duo: false,
        booking_amount: 2,
        venue: {
          identifier: 'KF',
          name: 'Librairie Kléber'
        }
      },
    ]

    // when
    const result = generateBookingsCsvFile(bookings)

    // then
    expect(result).toStrictEqual([
      CSV_HEADERS,
      [
        'La FNAC Lyon',
        "Avez-vous \"\"déjà\"\" \"\"vu\"\"",
        '',
        '9781234567654',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '03/04/2020 12:00',
        'ZEHBGD',
        1,
        'validé',
      ],
      [
        'Librairie Kléber',
        "Jurassic \"\"Park\"\"",
        '',
        '',
        'LaGuez Anthony',
        'anthony.laguez@example.com',
        '01/05/2020 14:12',
        'ABCDEF',
        2,
        'annulé',
      ],
    ])
  })

  it('should return data with all bookings using offerer name when venue is virtual', () => {
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
        booking_amount: 2,
        offerer: {
          name: 'Le conseil des librairies'
        },
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber',
          is_virtual: false
        }
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
        booking_amount: 5,
        offerer: {
          name: 'Le conseil des FNAC'
        },
        venue: {
          identifier: 'AB',
          name: 'La FNAC Lyon',
          is_virtual: true
        }
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
        '12/05/2020 11:03',
        '',
        'Klepi Sonia',
        'sonia.klepi@example.com',
        '03/04/2020 12:00',
        'ZEHBGD',
        2,
        'validé',
      ],
      [
        'Le conseil des FNAC - Offre numérique',
        'Jurassic Park',
        '',
        '',
        'LaMerguez Daniel',
        'daniel.lamerguez@example.com',
        '01/05/2020 14:12',
        'ABCDEF',
        5,
        'annulé',
      ],
    ])
  })
})

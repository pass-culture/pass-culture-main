import filterBookingsRecap from '../filterBookingsRecap'
import { EMPTY_FILTER_VALUE } from '../../Filters/_constants'

describe('filterBookingsRecap', () => {
  it('should return list when no filters provided', () => {
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
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber'
        }
      },
    ]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching offerName keywords', () => {
    // given
    const bookingRecap1 = {
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
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: 'Merlin',
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should not return element when BookingRecap is a thing and search with offerDate', () => {
    // given
    const bookingRecap = {
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
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap]
    const filters = {
      offerName: EMPTY_FILTER_VALUE,
      offerDate: '2020-02-18',
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([])
  })

  it('should return list containing only BookingRecap matching given offerDate', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        event_beginning_datetime: '2020-03-03T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: '2020-01-14',
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
  })

  it('should return list containing only BookingRecap matching given booking beginning date period', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        event_beginning_datetime: '2020-03-03T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-01-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: '2020-01-14',
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
  })

  it('should return list containing only BookingRecap matching given booking beginning date started on same day', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        event_beginning_datetime: '2020-03-03T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-01-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: '2020-02-18',
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
  })

  it('should return list containing only BookingRecap matching given booking end date period', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        event_beginning_datetime: '2020-03-03T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-01-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: '2020-01-14',
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching given booking date in given period', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        event_beginning_datetime: '2020-03-03T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-01-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: '2020-01-01',
      bookingEndingDate: '2020-01-14',
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching given offerDate and offerName', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-18T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: '2020-01-14',
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: 'Jurrasic',
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
  })

  it('should return list containing only BookingRecap matching given offerVenue', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-18T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        event_beginning_datetime: '2020-01-14T12:00:00Z',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-02-18T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AF',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: 'AE',
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching beneficiary name or email keywords', () => {
    // given
    const bookingRecap1 = {
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
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Ludovic',
        email: 'ludovic.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: 'Ludovic',
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
  })

  it('should return list containing only BookingRecap matching ISBN keywords', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        offer_isbn: '9787605639121',
        type: 'book',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: '98454627263',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        offer_isbn: '1234567890',
        type: 'book',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Ludovic',
        email: 'ludovic.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerISBN: '9787605',
      offerName: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching token keywords', () => {
    // given
    const bookingRecap1 = {
      stock: {
        offer_name: 'Merlin enchanteur',
        offer_isbn: '9787605639121',
        type: 'book',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ABCDEF',
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecap2 = {
      stock: {
        offer_name: 'Jurrasic Perk',
        type: 'thing',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Ludovic',
        email: 'ludovic.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZACBGD',
      booking_status: 'Remboursé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingRecapWithNoToken = {
      stock: {
        offer_name: 'Jurrasic Perk',
        type: 'thing',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Ludovic',
        email: 'ludovic.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: null,
      booking_status: 'Validé',
      venue: {
        identifier: 'AE',
        name: 'Librairie Kléber'
      }
    }
    const bookingsRecap = [bookingRecap1, bookingRecap2, bookingRecapWithNoToken]
    const filters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: 'abc',
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
    }

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })
})

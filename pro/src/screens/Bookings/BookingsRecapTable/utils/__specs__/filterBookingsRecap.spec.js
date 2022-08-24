import { EMPTY_FILTER_VALUE } from '../../components/Filters/_constants'
import filterBookingsRecap from '../filterBookingsRecap'

const bookingRecapBuilder = ({
  stock_offer_name = 'Merlin enchanteur',
  stock_offer_isbn = '9787605639121',
  stock_event_beginning_datetime = '2020-03-03T12:00:00Z',
  stock_type = 'event',
  beneficiary_lastname = 'Klepi',
  beneficiary_firstname = 'Sonia',
  beneficiary_email = 'sonia.klepi@example.com',
  booking_date = '2020-04-03T12:00:00Z',
  booking_token = 'ZEHBGD',
  booking_status = 'Validé',
  venue_identifier = 'AE',
  venue_name = 'Librairie Kléber',
}) => ({
  stock: {
    offer_name: stock_offer_name,
    offer_isbn: stock_offer_isbn,
    event_beginning_datetime: stock_event_beginning_datetime,
    type: stock_type,
  },
  beneficiary: {
    lastname: beneficiary_lastname,
    firstname: beneficiary_firstname,
    email: beneficiary_email,
  },
  booking_date: booking_date,
  booking_token: booking_token,
  booking_status: booking_status,
  venue: {
    identifier: venue_identifier,
    name: venue_name,
  },
})

const filtersBuilder = ({
  bookingBeneficiary = EMPTY_FILTER_VALUE,
  bookingToken = EMPTY_FILTER_VALUE,
  bookingBeginningDate = EMPTY_FILTER_VALUE,
  bookingEndingDate = EMPTY_FILTER_VALUE,
  offerDate = EMPTY_FILTER_VALUE,
  offerISBN = EMPTY_FILTER_VALUE,
  offerName = EMPTY_FILTER_VALUE,
  offerVenue = EMPTY_FILTER_VALUE,
}) => ({
  bookingBeneficiary: bookingBeneficiary,
  bookingToken: bookingToken,
  bookingBeginningDate: bookingBeginningDate,
  bookingEndingDate: bookingEndingDate,
  offerDate: offerDate,
  offerISBN: offerISBN,
  offerName: offerName,
  offerVenue: offerVenue,
})

describe('filterBookingsRecap', () => {
  it('should return list when no filters provided', () => {
    // given
    const bookingsRecap = [bookingRecapBuilder({})]
    const filters = filtersBuilder({})

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  describe('by offer name', () => {
    it('should return list containing only BookingRecap matching keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        stock_offer_name: 'Jurrasic Perk',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]

      let filters = filtersBuilder({ offerName: 'Merlin' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching keywords with different accents', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        stock_offer_name: 'Jurrasic Perk',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ offerName: 'Mérlin' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching keywords with different case', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({})
      bookingRecap2.stock.offer_name = 'Jurrasic Perk'
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ offerName: 'MerlIN' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching keywords with uppercase letters', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        stock_offer_name: 'Jurrasic Perk',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ offerName: 'MerlIN' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })
  })

  describe('by token', () => {
    it('should return list containing only BookingRecap matching token keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({ booking_token: 'ABCDEF' })
      const bookingRecap2 = bookingRecapBuilder({ booking_token: 'ZACBGQ' })
      const bookingRecapWithNoToken = bookingRecapBuilder({
        booking_token: null,
      })
      const bookingsRecap = [
        bookingRecap1,
        bookingRecap2,
        bookingRecapWithNoToken,
      ]
      const filters = filtersBuilder({ bookingToken: 'abc' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching token keywords with surrounding space', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({ booking_token: 'ABCDEF' })
      const bookingRecap2 = bookingRecapBuilder({ booking_token: 'ZACBGD' })
      const bookingRecapWithNoToken = bookingRecapBuilder({
        booking_token: null,
      })
      const bookingsRecap = [
        bookingRecap1,
        bookingRecap2,
        bookingRecapWithNoToken,
      ]
      const filters = filtersBuilder({ bookingToken: 'abc ' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching token keywords with different case', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({ booking_token: 'ABCDEF' })
      const bookingRecap2 = bookingRecapBuilder({ booking_token: 'ZACBGQ' })
      const bookingRecapWithNoToken = bookingRecapBuilder({
        booking_token: null,
      })
      const bookingsRecap = [
        bookingRecap1,
        bookingRecap2,
        bookingRecapWithNoToken,
      ]
      const filters = filtersBuilder({ bookingToken: 'aBc' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })
  })

  describe('by ISBN', () => {
    it('should return list containing only BookingRecap matching ISBN keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({ stock_type: 'book' })
      const bookingRecap2 = bookingRecapBuilder({
        stock_offer_isbn: '0864645534',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ offerISBN: '9787605639121' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching ISBN keywords with surrounding space', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({ stock_type: 'book' })
      const bookingRecap2 = bookingRecapBuilder({
        stock_offer_isbn: '0864645534',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ offerISBN: '9787605639121  ' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })
  })

  describe('by beneficiary', () => {
    it('should return list containing only BookingRecap matching beneficiary firstname keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_firstname: 'Ludovic',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Ludovic' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching partial beneficiary firstname keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_firstname: 'Ludovic',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Ludov' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching beneficiary lastname keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_lastname: 'Dupont',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Dupont' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching partial beneficiary lastname keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_lastname: 'Dupont',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Dup' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching beneficiary email keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_email: 'ludo@example.com',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({
        bookingBeneficiary: 'sonia.klepi@example.com',
      })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching partial beneficiary email keywords', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_email: 'ludovic@example.com',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({
        bookingBeneficiary: 'ludovic@example.c',
      })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching beneficiary firstname lastname in that order', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_firstname: 'Ludovic',
        beneficiary_lastname: 'Klepi',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Ludovic Klepi' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap2])
    })

    it('should return list containing only BookingRecap matching beneficiary lastname firstname in that order', () => {
      // given
      const bookingRecap1 = bookingRecapBuilder({})
      const bookingRecap2 = bookingRecapBuilder({
        beneficiary_firstname: 'Ludovic',
      })
      const bookingsRecap = [bookingRecap1, bookingRecap2]
      const filters = filtersBuilder({ bookingBeneficiary: 'Klepi Sonia' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should escape accents', () => {
      // given
      const bookingRecap = bookingRecapBuilder({})
      const bookingsRecap = [bookingRecap]
      const filters = filtersBuilder({ bookingBeneficiary: 'Klépi Sonià' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap])
    })

    it('should trim input', () => {
      // given
      const bookingRecap = bookingRecapBuilder({})
      const bookingsRecap = [bookingRecap]
      const filters = filtersBuilder({ bookingBeneficiary: 'Klepi Sonia' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap])
    })
  })
})

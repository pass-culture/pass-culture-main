import { bookingRecapFactory } from 'utils/apiFactories'

import { EMPTY_FILTER_VALUE } from '../../components/Filters/_constants'
import filterBookingsRecap from '../filterBookingsRecap'

const filtersBuilder = ({
  bookingBeneficiary = EMPTY_FILTER_VALUE,
  bookingToken = EMPTY_FILTER_VALUE,
  bookingBeginningDate = EMPTY_FILTER_VALUE,
  bookingEndingDate = EMPTY_FILTER_VALUE,
  offerDate = EMPTY_FILTER_VALUE,
  offerISBN = EMPTY_FILTER_VALUE,
  offerName = EMPTY_FILTER_VALUE,
  offerVenue = EMPTY_FILTER_VALUE,
  bookingId = EMPTY_FILTER_VALUE,
}) => ({
  bookingBeneficiary: bookingBeneficiary,
  bookingToken: bookingToken,
  bookingBeginningDate: bookingBeginningDate,
  bookingEndingDate: bookingEndingDate,
  offerDate: offerDate,
  offerISBN: offerISBN,
  offerName: offerName,
  offerVenue: offerVenue,
  bookingId: bookingId,
})

describe('filterBookingsRecap', () => {
  it('should return list when no filters provided', () => {
    // given
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({})

    // when
    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    // then
    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  describe('by offer name', () => {
    it('should return list containing only BookingRecap matching keywords', () => {
      // given

      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]

      let filters = filtersBuilder({ offerName: 'Le nom de l’offre' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with different accents', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'Lé nom de l’öffre ' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with different case', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'Le nom de l’OFfRE' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with uppercase letters', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'LE NOM DE L’OFFRE' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })
  })

  describe('by token', () => {
    it('should return list containing only BookingRecap matching token keywords', () => {
      // given
      const bookingRecap1 = bookingRecapFactory({ bookingToken: 'ABCDEF' })
      const bookingRecap2 = bookingRecapFactory({ bookingToken: 'ZACBGQ' })
      const bookingRecapWithNoToken = bookingRecapFactory({
        bookingToken: null,
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
      const bookingRecap1 = bookingRecapFactory({ bookingToken: 'ABCDEF' })
      const bookingRecap2 = bookingRecapFactory({ bookingToken: 'ZACBGD' })
      const bookingRecapWithNoToken = bookingRecapFactory({
        bookingToken: null,
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
      const bookingRecap1 = bookingRecapFactory({ bookingToken: 'ABCDEF' })
      const bookingRecap2 = bookingRecapFactory({ bookingToken: 'ZACBGQ' })
      const bookingRecapWithNoToken = bookingRecapFactory({
        bookingToken: null,
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
      const bookingRecap1 = bookingRecapFactory({
        stock_type: 'book',
      })

      const bookingsRecap = [bookingRecap1]
      const filters = filtersBuilder({ offerISBN: '123456789' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })

    it('should return list containing only BookingRecap matching ISBN keywords with surrounding space', () => {
      // given
      const bookingRecap1 = bookingRecapFactory({ stock_type: 'book' })

      const bookingsRecap = [bookingRecap1]
      const filters = filtersBuilder({ offerISBN: '123456789  ' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
    })
  })

  describe('by beneficiary', () => {
    it('should return list containing only BookingRecap matching beneficiary firstname keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'Last' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching partial beneficiary firstname keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'Las' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching beneficiary lastname keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'Last' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching partial beneficiary lastname keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'Las' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching beneficiary email keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({
        bookingBeneficiary: 'user@example.com',
      })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching partial beneficiary email keywords', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({
        bookingBeneficiary: 'user@example',
      })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching beneficiary firstname lastname in that order', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching beneficiary lastname firstname in that order', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should escape accents', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'Fïrst Làst' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should trim input', () => {
      // given
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

      // when
      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      // then
      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })
  })
})

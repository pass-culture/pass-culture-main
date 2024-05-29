import { bookingRecapFactory } from 'utils/individualApiFactories'

import { EMPTY_FILTER_VALUE } from '../../Filters/constants'
import { BookingsFilters } from '../../types'
import { filterBookingsRecap } from '../filterBookingsRecap'

const filtersBuilder = ({
  bookingBeneficiary = EMPTY_FILTER_VALUE,
  bookingToken = EMPTY_FILTER_VALUE,
  offerISBN = EMPTY_FILTER_VALUE,
  offerName = EMPTY_FILTER_VALUE,
  bookingId = EMPTY_FILTER_VALUE,
}): BookingsFilters => ({
  bookingBeneficiary: bookingBeneficiary,
  bookingToken: bookingToken,
  offerISBN: offerISBN,
  offerName: offerName,
  bookingId: bookingId,
  bookingStatus: [],
  selectedOmniSearchCriteria: '',
  keywords: '',
  bookingInstitution: '',
})

describe('filterBookingsRecap', () => {
  it('should return list when no filters provided', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({})

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  describe('by offer name', () => {
    it('should return list containing only BookingRecap matching keywords', () => {
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'Le nom de l’offre' })

      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with different accents', () => {
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'Lé nom de l’öffre ' })

      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with different case', () => {
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'Le nom de l’OFfRE' })

      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })

    it('should return list containing only BookingRecap matching keywords with uppercase letters', () => {
      const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
      const filters = filtersBuilder({ offerName: 'LE NOM DE L’OFFRE' })

      const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

      expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
    })
  })

  it('should return list containing only BookingRecap matching token keywords', () => {
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

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching token keywords with surrounding space', () => {
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

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching token keywords with different case', () => {
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

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching ISBN keywords', () => {
    const bookingRecap1 = bookingRecapFactory()

    const bookingsRecap = [bookingRecap1]
    const filters = filtersBuilder({ offerISBN: '123456789' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching ISBN keywords with surrounding space', () => {
    const bookingRecap1 = bookingRecapFactory()
    const bookingsRecap = [bookingRecap1]
    const filters = filtersBuilder({ offerISBN: '123456789  ' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
  })

  it('should return list containing only BookingRecap matching beneficiary firstname keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'Last' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching partial beneficiary firstname keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'Las' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching beneficiary lastname keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'Last' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching partial beneficiary lastname keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'Las' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching beneficiary email keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({
      bookingBeneficiary: 'user@example.com',
    })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching partial beneficiary email keywords', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({
      bookingBeneficiary: 'user@example',
    })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching beneficiary firstname lastname in that order', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should return list containing only BookingRecap matching beneficiary lastname firstname in that order', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should escape accents', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'Fïrst Làst' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })

  it('should trim input', () => {
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const filters = filtersBuilder({ bookingBeneficiary: 'First Last' })

    const filteredBookingsRecap = filterBookingsRecap(bookingsRecap, filters)

    expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
  })
})

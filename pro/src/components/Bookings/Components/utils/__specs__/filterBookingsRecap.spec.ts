import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'

import { EMPTY_FILTER_VALUE } from '../../Filters/constants'
import type { BookingsFilters } from '../../types'
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
    it.each([
      { description: 'matching keywords', offerName: "Le nom de l'offre" },
      {
        description: 'matching keywords with different accents',
        offerName: "Lé nom de l'öffre ",
      },
      {
        description: 'matching keywords with different case',
        offerName: "Le nom de l'OFfRE",
      },
      {
        description: 'matching keywords with uppercase letters',
        offerName: "LE NOM DE L'OFFRE",
      },
    ])(
      'should return list containing only BookingRecap $description',
      ({ offerName }) => {
        const bookingsRecap = [
          bookingRecapFactory({
            stock: bookingRecapStockFactory({ offerName: "Le nom de l'offre" }),
          }),
          bookingRecapFactory({
            stock: bookingRecapStockFactory({ offerName: "Le nom de l'offre" }),
          }),
        ]
        const filters = filtersBuilder({ offerName })

        const filteredBookingsRecap = filterBookingsRecap(
          bookingsRecap,
          filters
        )

        expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
      }
    )
  })

  describe('by booking token', () => {
    it.each([
      { description: 'matching keywords', bookingToken: 'abc' },
      {
        description: 'matching keywords with surrounding space',
        bookingToken: 'abc ',
      },
      {
        description: 'matching keywords with different case',
        bookingToken: 'aBc',
      },
    ])(
      'should return list containing only BookingRecap $description',
      ({ bookingToken }) => {
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
        const filters = filtersBuilder({ bookingToken })

        const filteredBookingsRecap = filterBookingsRecap(
          bookingsRecap,
          filters
        )

        expect(filteredBookingsRecap).toStrictEqual([bookingRecap1])
      }
    )
  })

  describe('by ISBN', () => {
    it.each([
      { description: 'matching keywords', offerISBN: '123456789' },
      {
        description: 'matching keywords with surrounding space',
        offerISBN: '123456789  ',
      },
    ])(
      'should return list containing only BookingRecap $description',
      ({ offerISBN }) => {
        const bookingsRecap = [bookingRecapFactory()]
        const filters = filtersBuilder({ offerISBN })

        const filteredBookingsRecap = filterBookingsRecap(
          bookingsRecap,
          filters
        )

        expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
      }
    )
  })

  describe('by beneficiary', () => {
    it.each([
      {
        description: 'matching firstname keywords',
        bookingBeneficiary: 'First',
      },
      {
        description: 'matching partial firstname keywords',
        bookingBeneficiary: 'Fir',
      },
      { description: 'matching lastname keywords', bookingBeneficiary: 'Last' },
      {
        description: 'matching partial lastname keywords',
        bookingBeneficiary: 'Las',
      },
      {
        description: 'matching email keywords',
        bookingBeneficiary: 'user@example.com',
      },
      {
        description: 'matching partial email keywords',
        bookingBeneficiary: 'user@example',
      },
      {
        description: 'matching firstname lastname in that order',
        bookingBeneficiary: 'First Last',
      },
      {
        description: 'matching lastname firstname in that order',
        bookingBeneficiary: 'Last First',
      },
      { description: 'escaping accents', bookingBeneficiary: 'Fïrst Làst' },
      { description: 'trimming input', bookingBeneficiary: ' First Last ' },
    ])(
      'should return list containing only BookingRecap $description',
      ({ bookingBeneficiary }) => {
        const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
        const filters = filtersBuilder({ bookingBeneficiary })

        const filteredBookingsRecap = filterBookingsRecap(
          bookingsRecap,
          filters
        )

        expect(filteredBookingsRecap).toStrictEqual(bookingsRecap)
      }
    )
  })
})

import {
  collectiveBookingCollectiveStockFactory,
  collectiveBookingFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { bookingRecapFactory } from '@/commons/utils/factories/individualApiFactories'

import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from '../sortingFunctions'

describe('sortByOfferName', () => {
  it('should return 1 when first row offer name comes after second row offer name', () => {
    const bookingA = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Zebre du Bengal',
      }),
    })
    const bookingB = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Babar, mon ami éléphant',
      }),
    })

    const result = sortByOfferName(bookingA, bookingB)

    expect(result).toBe(1)
  })

  it('should return -1 when first row offer name comes before second row offer name', () => {
    const bookingA = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Babar, mon ami éléphant',
      }),
    })
    const bookingB = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Zebre du Bengal',
      }),
    })

    const result = sortByOfferName(bookingA, bookingB)

    expect(result).toBe(-1)
  })

  it('should return 0 when first row offer name is the same as second row offer name', () => {
    const bookingA = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Babar, mon ami éléphant',
      }),
    })
    const bookingB = collectiveBookingFactory({
      stock: collectiveBookingCollectiveStockFactory({
        offerName: 'Babar, mon ami éléphant',
      }),
    })

    const result = sortByOfferName(bookingA, bookingB)

    expect(result).toBe(0)
  })
})

describe('sortByBookingDate', () => {
  it('should return -1 when first row bookingDate comes before second row bookingDate', () => {
    const bookingA = collectiveBookingFactory({
      bookingDate: '2020-04-22T11:17:12+02:00',
    })
    const bookingB = collectiveBookingFactory({
      bookingDate: '2020-04-23T13:17:12+02:00',
    })

    const result = sortByBookingDate(bookingA, bookingB)

    expect(result).toBe(-1)
  })

  it('should return 1 when first row bookingDate comes after second row bookingDate', () => {
    const bookingA = collectiveBookingFactory({
      bookingDate: '2020-04-22T11:17:12+02:00',
    })
    const bookingB = collectiveBookingFactory({
      bookingDate: '2020-04-22T12:16:12+03:00',
    })

    const result = sortByBookingDate(bookingA, bookingB)

    expect(result).toBe(1)
  })

  it('should return 0 when first row bookingDate is the same as second row bookingDate', () => {
    const bookingA = collectiveBookingFactory({
      bookingDate: '2020-04-22T11:17:12+02:00',
    })
    const bookingB = collectiveBookingFactory({
      bookingDate: '2020-04-22T11:17:12+02:00',
    })

    const result = sortByBookingDate(bookingA, bookingB)

    expect(result).toBe(0)
  })
})

describe('sortByBeneficiaryName', () => {
  it('should return 1 when 1st row beneficiary name strictly comes after 2nd row beneficiary name', () => {
    const bookingA = bookingRecapFactory({
      beneficiary: {
        lastname: 'Gamgee',
        firstname: 'Samwise',
      },
    })
    const bookingB = bookingRecapFactory({
      beneficiary: {
        lastname: 'Baggings',
        firstname: 'Bilbo',
      },
    })

    const result = sortByBeneficiaryName(bookingA, bookingB)

    expect(result).toBe(1)
  })

  it('should return -1 when 1st row beneficiary name strictly comes before 2nd row beneficiary name', () => {
    const bookingA = bookingRecapFactory({
      beneficiary: {
        lastname: 'Baggings',
        firstname: 'Bilbo',
      },
    })
    const bookingB = bookingRecapFactory({
      beneficiary: {
        lastname: 'Gamgee',
        firstname: 'Samwise',
      },
    })

    const result = sortByBeneficiaryName(bookingA, bookingB)

    expect(result).toBe(-1)
  })

  describe('when both beneficiaries lastname are the same', () => {
    it('should return 1 when 1st row beneficiary firstname comes after 2nd row beneficiary firstname', () => {
      const bookingA = bookingRecapFactory({
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Samwise',
        },
      })
      const bookingB = bookingRecapFactory({
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Rosie',
        },
      })

      const result = sortByBeneficiaryName(bookingA, bookingB)

      expect(result).toBe(1)
    })

    it('should return -1 when 1st row beneficiary firstname comes before 2nd row beneficiary firstname', () => {
      const bookingA = bookingRecapFactory({
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Rosie',
        },
      })
      const bookingB = bookingRecapFactory({
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Samwise',
        },
      })

      const result = sortByBeneficiaryName(bookingA, bookingB)

      expect(result).toBe(-1)
    })

    it('should return 0 if lastname and firstname are the same even with different case', () => {
      const bookingA = bookingRecapFactory({
        beneficiary: {
          lastname: 'Durand',
          firstname: 'Aragorn',
        },
      })
      const bookingB = bookingRecapFactory({
        beneficiary: {
          lastname: 'Durand',
          firstname: 'aragorn',
        },
      })

      const result = sortByBeneficiaryName(bookingA, bookingB)

      expect(result).toBe(0)
    })
  })
})

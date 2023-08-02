import { Row } from 'react-table'

import { BookingRecapResponseModel } from 'apiClient/v1'

import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from '../sortingFunctions'

describe('sortByOfferName', () => {
  it('should return 1 when first row offer name comes after second row offer name', () => {
    const firstRow = {
      original: {
        stock: {
          offerName: 'Zebre du Bengal',
        },
      },
    } as Row<BookingRecapResponseModel>

    const secondRow = {
      original: {
        stock: {
          offerName: 'Babar, mon ami éléphant',
        },
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByOfferName(firstRow, secondRow)

    expect(result).toBe(1)
  })

  it('should return -1 when first row offer name comes before second row offer name', () => {
    const firstRow = {
      original: {
        stock: {
          offerName: 'Babar, mon ami éléphant',
        },
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        stock: {
          offerName: 'Zebre du Bengal',
        },
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByOfferName(firstRow, secondRow)

    expect(result).toBe(-1)
  })

  it('should return 0 when first row offer name is the same as second row offer name', () => {
    const firstRow = {
      original: {
        stock: {
          offerName: 'Babar, mon ami éléphant',
        },
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        stock: {
          offerName: 'Babar, mon ami éléphant',
        },
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByOfferName(firstRow, secondRow)

    expect(result).toBe(0)
  })
})

describe('sortByBookingDate', () => {
  it('should return -1 when first row bookingDate comes before second row bookingDate', () => {
    const firstRow = {
      original: {
        bookingDate: '2020-04-22T11:17:12+02:00',
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        bookingDate: '2020-04-23T13:17:12+02:00',
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByBookingDate(firstRow, secondRow)

    expect(result).toBe(-1)
  })

  it('should return 1 when first row bookingDate comes after second row bookingDate', () => {
    const firstRow = {
      original: {
        bookingDate: '2020-04-22T11:17:12+02:00',
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        bookingDate: '2020-04-22T12:16:12+03:00',
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByBookingDate(firstRow, secondRow)

    expect(result).toBe(1)
  })

  it('should return 0 when first row bookingDate is the same as second row bookingDate', () => {
    const firstRow = {
      original: {
        bookingDate: '2020-04-22T11:17:12+02:00',
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        bookingDate: '2020-04-22T11:17:12+02:00',
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByBookingDate(firstRow, secondRow)

    expect(result).toBe(0)
  })
})

describe('sortByBeneficiaryName', () => {
  it('should return 1 when 1st row beneficiary name strictly comes after 2nd row beneficiary name', () => {
    const firstRow = {
      original: {
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Samwise',
        },
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        beneficiary: {
          lastname: 'Baggings',
          firstname: 'Bilbo',
        },
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByBeneficiaryName(firstRow, secondRow)

    expect(result).toBe(1)
  })

  it('should return -1 when 1st row beneficiary name strictly comes before 2nd row beneficiary name', () => {
    const firstRow = {
      original: {
        beneficiary: {
          lastname: 'Baggings',
          firstname: 'Bilbo',
        },
      },
    } as Row<BookingRecapResponseModel>
    const secondRow = {
      original: {
        beneficiary: {
          lastname: 'Gamgee',
          firstname: 'Samwise',
        },
      },
    } as Row<BookingRecapResponseModel>

    const result = sortByBeneficiaryName(firstRow, secondRow)

    expect(result).toBe(-1)
  })

  describe('when both beneficiaries lastname are the same', () => {
    it('should return 1 when 1st row beneficiary firstname comes after 2nd row beneficiary firstname', () => {
      const firstRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Samwise',
          },
        },
      } as Row<BookingRecapResponseModel>
      const secondRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Rosie',
          },
        },
      } as Row<BookingRecapResponseModel>

      const result = sortByBeneficiaryName(firstRow, secondRow)

      expect(result).toBe(1)
    })

    it('should return -1 when 1st row beneficiary firstname comes before 2nd row beneficiary firstname', () => {
      const firstRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Rosie',
          },
        },
      } as Row<BookingRecapResponseModel>
      const secondRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Samwise',
          },
        },
      } as Row<BookingRecapResponseModel>

      const result = sortByBeneficiaryName(firstRow, secondRow)

      expect(result).toBe(-1)
    })

    it('should return 0 if lastname and firstname are the same even with different case', () => {
      const firstRow = {
        original: {
          beneficiary: {
            lastname: 'Durand',
            firstname: 'Aragorn',
          },
        },
      } as Row<BookingRecapResponseModel>
      const secondRow = {
        original: {
          beneficiary: {
            lastname: 'Durand',
            firstname: 'aragorn',
          },
        },
      } as Row<BookingRecapResponseModel>

      const result = sortByBeneficiaryName(firstRow, secondRow)

      expect(result).toBe(0)
    })
  })
})

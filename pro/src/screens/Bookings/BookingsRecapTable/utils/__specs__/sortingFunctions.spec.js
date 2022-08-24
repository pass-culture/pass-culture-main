import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from '../sortingFunctions'

describe('utils | sortingFunctions', () => {
  describe('sortByOfferName', () => {
    it('should return 1 when first row offer name comes after second row offer name', () => {
      // given
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Zebre du Bengal',
          },
        },
      }
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant',
          },
        },
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(1)
    })

    it('should return -1 when first row offer name comes before second row offer name', () => {
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant',
          },
        },
      }
      // given
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Zebre du Bengal',
          },
        },
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(-1)
    })

    it('should return 0 when first row offer name is the same as second row offer name', () => {
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant',
          },
        },
      }
      // given
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant',
          },
        },
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(0)
    })
  })

  describe('sortByBookingDate', () => {
    it('should return -1 when first row bookingDate comes before second row bookingDate', () => {
      // given
      const firstRow = {
        original: {
          booking_date: '2020-04-22T11:17:12+02:00',
        },
      }
      const secondRow = {
        original: {
          booking_date: '2020-04-23T13:17:12+02:00',
        },
      }

      // when
      const result = sortByBookingDate(firstRow, secondRow)

      // then
      expect(result).toBe(-1)
    })

    it('should return 1 when first row bookingDate comes after second row bookingDate', () => {
      // given
      const firstRow = {
        original: {
          booking_date: '2020-04-22T11:17:12+02:00',
        },
      }
      const secondRow = {
        original: {
          booking_date: '2020-04-22T12:16:12+03:00',
        },
      }

      // when
      const result = sortByBookingDate(firstRow, secondRow)

      // then
      expect(result).toBe(1)
    })

    it('should return 0 when first row bookingDate is the same as second row bookingDate', () => {
      const firstRow = {
        original: {
          booking_date: '2020-04-22T11:17:12+02:00',
        },
      }
      // given
      const secondRow = {
        original: {
          booking_date: '2020-04-22T11:17:12+02:00',
        },
      }

      // when
      const result = sortByBookingDate(firstRow, secondRow)

      // then
      expect(result).toBe(0)
    })
  })

  describe('sortByBeneficiaryName', () => {
    it('should return 1 when 1st row beneficiary name strictly comes after 2nd row beneficiary name', () => {
      // Given
      const firstRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Samwise',
          },
        },
      }
      const secondRow = {
        original: {
          beneficiary: {
            lastname: 'Baggings',
            firstname: 'Bilbo',
          },
        },
      }

      // When
      const result = sortByBeneficiaryName(firstRow, secondRow)

      // Then
      expect(result).toBe(1)
    })

    it('should return -1 when 1st row beneficiary name strictly comes before 2nd row beneficiary name', () => {
      // Given
      const firstRow = {
        original: {
          beneficiary: {
            lastname: 'Baggings',
            firstname: 'Bilbo',
          },
        },
      }
      const secondRow = {
        original: {
          beneficiary: {
            lastname: 'Gamgee',
            firstname: 'Samwise',
          },
        },
      }

      // When
      const result = sortByBeneficiaryName(firstRow, secondRow)

      // Then
      expect(result).toBe(-1)
    })

    describe('when both beneficiaries lastname are the same', () => {
      it('should return 1 when 1st row beneficiary firstname comes after 2nd row beneficiary firstname', () => {
        // Given
        const firstRow = {
          original: {
            beneficiary: {
              lastname: 'Gamgee',
              firstname: 'Samwise',
            },
          },
        }
        const secondRow = {
          original: {
            beneficiary: {
              lastname: 'Gamgee',
              firstname: 'Rosie',
            },
          },
        }

        // When
        const result = sortByBeneficiaryName(firstRow, secondRow)

        // Then
        expect(result).toBe(1)
      })

      it('should return -1 when 1st row beneficiary firstname comes before 2nd row beneficiary firstname', () => {
        // Given
        const firstRow = {
          original: {
            beneficiary: {
              lastname: 'Gamgee',
              firstname: 'Rosie',
            },
          },
        }
        const secondRow = {
          original: {
            beneficiary: {
              lastname: 'Gamgee',
              firstname: 'Samwise',
            },
          },
        }

        // When
        const result = sortByBeneficiaryName(firstRow, secondRow)

        // Then
        expect(result).toBe(-1)
      })

      it('should return 0 if lastname and firstname are the same even with different case', () => {
        // Given
        const firstRow = {
          original: {
            beneficiary: {
              lastname: 'Durand',
              firstname: 'Aragorn',
            },
          },
        }
        const secondRow = {
          original: {
            beneficiary: {
              lastname: 'Durand',
              firstname: 'aragorn',
            },
          },
        }

        // When
        const result = sortByBeneficiaryName(firstRow, secondRow)

        // Then
        expect(result).toBe(0)
      })
    })
  })
})

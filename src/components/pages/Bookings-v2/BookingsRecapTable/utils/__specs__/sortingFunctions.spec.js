import { sortByBeneficiaryName, sortByOfferName } from '../sortingFunctions'

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

      it('should return 0 if lastname and firstname are the same', () => {
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
              firstname: 'Aragorn',
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

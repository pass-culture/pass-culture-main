import {
  selectVenues,
  selectPhysicalVenuesByOffererId,
  selectVenueById,
  selectVenuesByOffererId,
  selectNonVirtualVenues,
} from '../venuesSelectors'

describe('src | selectors | data | venuesSelectors', () => {
  describe('selectVenues', () => {
    describe('when venues attribute exists', () => {
      it('should return it', () => {
        const store = {
          data: {
            venues: [{ id: 1 }, { id: 2 }],
          },
        }
        expect(selectVenues(store)).toStrictEqual([{ id: 1 }, { id: 2 }])
      })
    })

    describe('when venues attribute does not not', () => {
      it('should return an empty array', () => {
        const store = {
          data: {},
        }
        expect(selectVenues(store)).toStrictEqual([])
      })
    })
  })

  describe('selectPhysicalVenuesByOffererId', () => {
    describe('when offerer Id is given', () => {
      it('should return non virtual venues with that offerer id', () => {
        const store = {
          data: {
            venues: [
              { id: 'AE', managingOffererId: 'ZZ', isVirtual: true },
              { id: 'AE', managingOffererId: 'ZZ', isVirtual: false },
              { id: 'AF', managingOffererId: 'AA', isVirtual: true },
              { id: 'AX', managingOffererId: 'AA', isVirtual: false },
            ],
          },
        }
        const offererId = 'ZZ'

        expect(selectPhysicalVenuesByOffererId(store, offererId)).toStrictEqual(
          [{ id: 'AE', managingOffererId: 'ZZ', isVirtual: false }]
        )
      })
    })

    describe('when offerer Id is not given', () => {
      it('should return non virtual venues without filtering by offerer Id', () => {
        const store = {
          data: {
            venues: [
              { id: 'AE', managingOffererId: 'ZZ', isVirtual: true },
              { id: 'AE', managingOffererId: 'ZZ', isVirtual: false },
              { id: 'AF', managingOffererId: 'AA', isVirtual: true },
              { id: 'AX', managingOffererId: 'ZZ', isVirtual: false },
            ],
          },
        }

        expect(selectPhysicalVenuesByOffererId(store)).toStrictEqual([
          { id: 'AE', managingOffererId: 'ZZ', isVirtual: false },
          { id: 'AX', managingOffererId: 'ZZ', isVirtual: false },
        ])
      })
    })
  })

  describe('selectVenueById', () => {
    describe('when venues is empty', () => {
      it('should return undefined', () => {
        const store = {
          data: {
            venues: [],
          },
        }
        expect(selectVenueById(store)).toBeUndefined()
      })
    })

    describe('when venue id is not given', () => {
      it('should return undefined', () => {
        const store = {
          data: {
            venues: [{ id: 'AE' }],
          },
        }
        expect(selectVenueById(store)).toBeUndefined()
      })
    })

    describe('when venue id doesnt exist in venues', () => {
      it('should return undefined', () => {
        const store = {
          data: {
            venues: [{ id: 'AE' }],
          },
        }
        expect(selectVenueById(store, 'B4')).toBeUndefined()
      })
    })

    describe('when venue id matches a venue', () => {
      it('should return it', () => {
        const store = {
          data: {
            venues: [{ id: 'AE' }],
          },
        }
        expect(selectVenueById(store, 'AE')).toStrictEqual({ id: 'AE' })
      })
    })
  })

  describe('selectVenuesByOffererId', () => {
    describe('when venues is empty', () => {
      it('should return an empty array', () => {
        const store = {
          data: {
            venues: [],
          },
        }
        expect(selectVenuesByOffererId(store)).toStrictEqual([])
      })
    })

    describe('when offerer id is not given', () => {
      it('should return all venues', () => {
        const store = {
          data: {
            venues: [
              { managingOffererId: 'AE' },
              {
                managingOfferer: {
                  id: 'AE',
                },
              },
            ],
          },
        }
        expect(selectVenuesByOffererId(store)).toStrictEqual([
          { managingOffererId: 'AE' },
          { managingOfferer: { id: 'AE' } },
        ])
      })
    })

    describe('when venue id doesnt exist in venues', () => {
      it('should return undefined', () => {
        const store = {
          data: {
            venues: [
              { managingOffererId: 'AE' },
              {
                managingOfferer: {
                  id: 'AE',
                },
              },
            ],
          },
        }
        expect(selectVenueById(store, 'B4')).toBeUndefined()
      })
    })

    describe('when venue id matches a venue', () => {
      it('should return it', () => {
        const store = {
          data: {
            venues: [
              { managingOffererId: 'AE' },
              {
                managingOfferer: {
                  id: 'AE',
                },
              },
            ],
          },
        }
        expect(selectVenuesByOffererId(store, 'AE')).toStrictEqual([
          { managingOffererId: 'AE' },
          { managingOfferer: { id: 'AE' } },
        ])
      })
    })
  })

  describe('selectNonVirtualVenues', () => {
    it('should return an empty list of non virtual venues when state contains no venues', () => {
      // given
      const state = {
        data: {
          venues: [],
        },
      }

      // when
      const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

      // then
      expect(nonVirtualVenuesToDisplay).toStrictEqual([])
    })

    it('should return only the non virtual venues', () => {
      // given
      const state = {
        data: {
          venues: [
            {
              id: 'A8HQ',
              isVirtual: true,
            },
            {
              id: 'A8RQ',
              isVirtual: false,
            },
            {
              id: 'AVGQ',
              isVirtual: false,
            },
          ],
        },
      }

      // when
      const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

      // then
      const nonVirtualVenuesListExpected = [
        {
          id: 'A8RQ',
          isVirtual: false,
        },
        {
          id: 'AVGQ',
          isVirtual: false,
        },
      ]

      expect(nonVirtualVenuesToDisplay).toStrictEqual(
        nonVirtualVenuesListExpected
      )
    })

    it('should return an empty list of offer when state is not initialized', () => {
      // given
      const state = {
        data: {},
      }

      // when
      const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

      // then
      const nonVirtualVenuesListExpected = []
      expect(nonVirtualVenuesToDisplay).toStrictEqual(
        nonVirtualVenuesListExpected
      )
    })
  })
})

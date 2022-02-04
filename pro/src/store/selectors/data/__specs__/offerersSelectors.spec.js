import { selectOfferers, selectOffererById } from '../offerersSelectors'

import state from './mockState.json'

describe('src | selectors | data | offerersSelectors', () => {
  describe('selectOfferers', () => {
    describe('when state data offerers exists', () => {
      it('should return it', () => {
        const state = {
          data: {
            offerers: [{ id: 1 }],
          },
        }
        expect(selectOfferers(state)).toStrictEqual([{ id: 1 }])
      })
    })
  })

  describe('selectOffererById', () => {
    describe('when offerers is empty', () => {
      it('should return undefined', () => {
        const state = {
          data: {
            offerers: [],
          },
        }
        expect(selectOffererById(state, 1)).toBeUndefined()
      })
    })

    describe('when offerer not found in data offerers array', () => {
      it('should return undefined', () => {
        const state = {
          data: {
            offerers: [{ id: 2 }],
          },
        }
        expect(selectOffererById(state, 1)).toBeUndefined()
      })
    })

    describe('when offerer found in data offerers array', () => {
      it('should return it', () => {
        const state = {
          data: {
            offerers: [{ id: 2 }],
          },
        }
        expect(selectOffererById(state, 2)).toStrictEqual({ id: 2 })
      })
    })

    it('should retrieve offerer from state when id is given', () => {
      // given
      const expected = {
        address: 'RUE DES SAPOTILLES',
        bic: 'QSDFGH8Z566',
        city: 'Cayenne',
        dateCreated: '2019-05-06T09:12:46.278743Z',
        dateModifiedAtLastProvider: '2019-05-06T09:13:08.458343Z',
        iban: 'FR7630001007941234567890185',
        id: '4Q',
        isActive: true,
        isValidated: true,
        lastProviderId: null,
        modelName: 'Offerer',
        nOffers: 5,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '222222233',
      }
      const offererId = '4Q'

      // when
      const result = selectOffererById(state, offererId)

      // then
      expect(result).toStrictEqual(expected)
    })
  })
})

import {
  selectTypeValueByOffer,
} from '../typesSelectors'

describe('src | selectors | data | typesSelectors', () => {
  describe('selectTypeValueByOffer', () => {
    it('should return pro label for offer type', () => {
      const offer = {
        id: 'ABCD',
        type: 'ThingType.Lapin'
      }
      const state = {
        data: {
          types: [
            {
              value: 'théâtre',
              proLabel: 'Théâtre'
            },
            {
              value: 'ThingType.Lapin',
              proLabel: 'Jeannot Lapin'
            }
          ],
        },
      }
      expect(selectTypeValueByOffer(state, offer)).toStrictEqual('Jeannot Lapin')
    })

    it('should return activation label for activation offer', () => {
      const offer = {
        id: 'ABCD',
        type: 'ThingType.ACTIVATION'
      }
      const state = {
        data: {
          types: [
            {
              value: 'théâtre',
              proLabel: 'Théâtre'
            },
            {
              value: 'ThingType.Lapin',
              proLabel: 'Jeannot Lapin'
            }
          ],
        },
      }
      expect(selectTypeValueByOffer(state, offer)).toStrictEqual('Pass Culture : activation')
    })
  })
})

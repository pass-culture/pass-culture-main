import { selectOfferers, selectOffererById } from '../offerersSelectors'

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
  })
})

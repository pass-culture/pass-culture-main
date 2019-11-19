import paginationReducer, { updatePage, updateSeed, updateSeedLastRequestTimestamp } from '../pagination'

describe('src | reducers | pagination', () => {
  describe('actions', () => {
    it('should return an action of type UPDATE_PAGE', () => {
      // given
      const page = 1

      // when
      const result = updatePage(page)

      // then
      expect(result).toStrictEqual({
        page: 1,
        type: 'UPDATE_PAGE'
      })
    })

    it('should return an action of type UPDATE_SEED', () => {
      // given
      const seed = 0.5

      // when
      const result = updateSeed(seed)

      // then
      expect(result).toStrictEqual({
        seed: 0.5,
        type: 'UPDATE_SEED'
      })
    })

    it('should return an action of type UPDATE_SEED_LAST_REQUEST_TIMESTAMP', () => {
      // given
      const timestamp = 1574186119058

      // when
      const result = updateSeedLastRequestTimestamp(timestamp)

      // then
      expect(result).toStrictEqual({
        seedLastRequestTimestamp: 1574186119058,
        type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP'
      })
    })
  })

  describe('reducers', () => {
    it('should return initial value when no action matches', () => {
      // when
      const nextState = paginationReducer()

      // then
      expect(nextState).toStrictEqual({
        page: 1,
        seed: expect.any(Number),
        seedLastRequestTimestamp: expect.any(Number)
      })
    })

    describe('when a UPDATE_PAGE action is received', () => {
      it('should update page to 2', () => {
        // when
        const nextState = paginationReducer({ page: 1, seed: 0.5, seedLastRequestTimestamp: 1574186119058 }, {
          page: 2,
          type: 'UPDATE_PAGE'
        })

        // then
        expect(nextState).toStrictEqual({
          page: 2,
          seed: 0.5,
          seedLastRequestTimestamp: 1574186119058
        })
      })
    })

    describe('when a UPDATE_SEED action is received', () => {
      it('should update seed to 0.5', () => {
        // when
        const nextState = paginationReducer({
          page: 1,
          seed: 0.1,
          seedLastRequestTimestamp: 1574186119058
        }, { seed: 0.5, type: 'UPDATE_SEED' })

        // then
        expect(nextState).toStrictEqual({
          page: 1,
          seed: 0.5,
          seedLastRequestTimestamp: 1574186119058
        })
      })
    })

    describe('when a UPDATE_SEED_LAST_REQUEST_TIMESTAMP action is received', () => {
      it('should update seed last request timestamp', () => {
        // when
        const nextState = paginationReducer(
          { page: 1, seed: 0.1, seedLastRequestTimestamp: 1574186119058 },
          { seedLastRequestTimestamp: 167283098390, type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP' }
        )

        // then
        expect(nextState).toStrictEqual({
          page: 1,
          seed: 0.1,
          seedLastRequestTimestamp: 167283098390
        })
      })
    })
  })
})

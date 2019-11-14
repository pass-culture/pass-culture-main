import paginationReducer, { updatePage, updateSeed } from '../pagination'

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
  })

  describe('reducers', () => {
    it('should return initial value when no action matches', () => {
      // when
      const nextState = paginationReducer()

      // then
      expect(nextState).toStrictEqual({
        page: 1,
        seed: expect.any(Number)
      })
    })

    describe('when a UPDATE_PAGE action is received', () => {
      it('should update page to 2', () => {
        // when
        const nextState = paginationReducer({ page: 1, seed: 0.5}, { page: 2, type: 'UPDATE_PAGE' })

        // then
        expect(nextState).toStrictEqual({
          page: 2,
          seed: 0.5
        })
      })
    })

    describe('when a UPDATE_SEED action is received', () => {
      it('should update seed to 0.5', () => {
        // when
        const nextState = paginationReducer({ page: 1, seed: 0.1}, { seed: 0.5, type: 'UPDATE_SEED' })

        // then
        expect(nextState).toStrictEqual({
          page: 1,
          seed: 0.5
        })
      })
    })
  })
})

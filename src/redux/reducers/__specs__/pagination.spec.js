import pagination from '../pagination'

describe('reducers | pagination', () => {
  it('should return initial value when no action matches', () => {
    // when
    const nextState = pagination()

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
      const nextState = pagination({ page: 1, seed: 0.5, seedLastRequestTimestamp: 1574186119058 }, {
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
      const nextState = pagination({
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
      const nextState = pagination(
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

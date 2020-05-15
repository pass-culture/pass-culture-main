import pagination from '../pagination'

describe('reducers | pagination', () => {
  it('should return initial value when no action matches', () => {
    // when
    const nextState = pagination()

    // then
    expect(nextState).toStrictEqual({
      seedLastRequestTimestamp: expect.any(Number),
    })
  })

  describe('when a UPDATE_SEED_LAST_REQUEST_TIMESTAMP action is received', () => {
    it('should update seed last request timestamp', () => {
      // when
      const nextState = pagination(
        { seedLastRequestTimestamp: 1574186119058 },
        { seedLastRequestTimestamp: 167283098390, type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP' }
      )

      // then
      expect(nextState).toStrictEqual({
        seedLastRequestTimestamp: 167283098390,
      })
    })
  })
})

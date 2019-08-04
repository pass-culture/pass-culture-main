import selectMediationById from '../selectMediationById'

describe('src | selectors | selectMediationById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        mediations: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectMediationById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return mediation matching id', () => {
    // given
    const state = {
      data: {
        mediations: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectMediationById(state, 'bar')

    // then
    expect(result).toBeDefined()
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.mediations[1])
  })
})

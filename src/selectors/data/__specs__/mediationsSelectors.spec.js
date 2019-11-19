import { selectMediationById, selectMediationByRouterMatch } from '../mediationsSelectors'

describe('selectMediationById', () => {
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
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.mediations[1])
  })
})

describe('selectMediationByRouterMatch', () => {
  it('should return mediation when mediationId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [],
      },
    }
    const match = {
      params: {
        mediationId: 'AE',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return mediation when bookingId in match resolves mediation', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'BF', mediationId: 'AE' }],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [{ id: 'AE' }],
      },
    }
    const match = {
      params: {
        bookingId: 'BF',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return mediation when favoriteId in match resolves mediation', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [{ id: 'BF', mediationId: 'AE' }],
        mediations: [{ id: 'AE' }],
        offers: [],
      },
    }
    const match = {
      params: {
        bookingId: 'AA',
        favoriteId: 'BF',
        mediationId: 'AE',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})

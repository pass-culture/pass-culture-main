import selectBookingById from '../selectBookingById'

describe('src | selectors | selectBookingById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectBookingById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return booking matching id', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectBookingById(state, 'bar')

    // then
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.bookings[1])
  })
})

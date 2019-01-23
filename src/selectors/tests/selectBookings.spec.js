import { selectBookingById } from '../selectBookings'

describe('src | selectors | selectBookings | selectBookingById', () => {
  it('should return booking matching id', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }
    // When
    const result = selectBookingById(state, 'bar')
    // Then
    expect(result).toBeDefined()
    expect(result).toEqual({ id: 'bar' })
    expect(result).toBe(state.data.bookings[1])
  })
})

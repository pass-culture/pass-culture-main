import { getBookingName } from '../VersoBookingButton'

describe('src | components | verso | getBookingName', () => {
  it('should return booking name', () => {
    // given
    const booking = {
      stock: {
        resolvedOffer: {
          eventOrThing: {
            name: 'foo',
          },
        },
      },
    }
    // when
    const result = getBookingName(booking)
    // then
    expect(result).toBeDefined()
    expect(result).toBe('foo')
  })
})

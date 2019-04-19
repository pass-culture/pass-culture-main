import { mapStateToProps } from '../MyBookingItemContainer'

describe('src | components | MyBookingItemContainer', () => {
  it('should map is_event', () => {
    // given
    const state = {
      data: {
        recommendations: [],
      },
    }
    const ownProps = {
      booking: {
        isCancelled: true,
        recommendationId: 'BJ2',
        stock: {
          resolvedOffer: {
            isEvent: true,
          },
        },
      },
    }

    // when
    const props = mapStateToProps(state, ownProps)

    // then
    expect(props).toHaveProperty('isEvent', true)
  })
})

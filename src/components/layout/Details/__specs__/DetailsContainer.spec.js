import { mapStateToProps } from '../DetailsContainer'

describe('src | components | layout | Details | DetailsContainer', () => {
  let ownProps
  let state

  beforeEach(() => {
    ownProps = {
      match: {
        params: {
          booking: 'reservation',
          confirmation: 'confirmation',
        },
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object confirming cancellation', () => {
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isConfirmingCancelling: true,
      })
    })

    it('should return an object not confirming cancellation', () => {
      // given
      ownProps.match.params.confirmation = undefined

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isConfirmingCancelling: false,
      })
    })
  })
})

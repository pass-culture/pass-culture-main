import { mapStateToProps } from '../VersoContainer'
import state from '../../../../mocks/state'

describe('src | components | layout | Verso | VersoContainer', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          bookingId: 'A9',
          offerId: 'AM',
        },
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        offerName: 'super offre',
        offerType: 'EventType.SPECTACLE_VIVANT',
        offerVenueNameOrPublicName: 'THEATRE DE L ODEON',
      })
    })
  })
})

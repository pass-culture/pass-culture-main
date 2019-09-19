import { mapStateToProps } from '../VersoContainer'
import reduxState from '../../../../mocks/reduxState'

describe('src | components | layout | Verso | VersoContainer', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          bookingId: 'CPGQ',
          offerId: 'AM',
        },
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(reduxState, props)

      // then
      expect(result).toStrictEqual({
        backgroundColor: 'black',
        contentInlineStyle: { backgroundImage: "url('http://localhost/mosaic-k.png')" },
        isTuto: false,
        offerName: 'super offre',
        offerType: 'EventType.SPECTACLE_VIVANT',
        offerVenueNameOrPublicName: 'THEATRE DE L ODEON',
      })
    })
  })
})

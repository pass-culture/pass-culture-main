import state from '../../../../../../../mocks/state'
import { mapStateToProps } from '../QrCodeContainer'

describe('src | components | pages | my-bookings | MyBookingsList | BookingList | QrCode | QrCodeContainer', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          bookingId: 'A9',
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
        humanizedBeginningDatetime: 'Vendredi 30/11/2018 à 22:42',
        offerName: 'super offre',
        qrCode: 'data:image/png;base64,iVIVhzdjeizfjezfoizejojczez',
        token: '2AEVY3',
        venueName: 'THEATRE DE L ODEON',
      })
    })
  })
})

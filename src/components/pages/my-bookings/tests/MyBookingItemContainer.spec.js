import moment from 'moment'
import 'moment/locale/fr'

import { mapStateToProps } from '../MyBookingItemContainer'

describe('src | components | MyBookingItemContainer', () => {
  it('should map object returned from mapStateToProps', () => {
    // given
    moment.locale('fr-fr')
    const token = 'BBBB'
    const offerId = 'CCCC'
    const isCancelled = true
    const mediationId = 'AAAA'
    const departementCode = '93'
    const name = 'name of this booking'
    const completedUrl = 'external.domain.url'
    const beginningDatetime = '2019-05-15T20:00:00Z'
    const thumbUrl = 'https://example.net/mediation/image'
    const ownProps = {
      booking: {
        completedUrl,
        isCancelled,
        recommendation: { mediationId, thumbUrl },
        stock: {
          beginningDatetime,
          resolvedOffer: {
            id: offerId,
            isEvent: true,
            product: { name },
            venue: { departementCode },
          },
        },
        token,
      },
    }

    // when
    const props = mapStateToProps({}, ownProps)

    // then
    const linkURL = `/decouverte/${offerId}/${mediationId}/verso`
    const dateString = 'Mercredi 15/05/2019 à 22:00'
    const expected = {
      completedUrl,
      cssClass: 'event',
      date: beginningDatetime,
      dateString,
      isCancelled,
      linkURL,
      name,
      thumbUrl,
      timezone: 'Europe/Paris',
      token,
    }
    expect(props).toStrictEqual(expected)
  })
})

import * as config from 'utils/config'
import { webappOfferUrl } from '../webappOfferUrl'

describe('src | webappOfferUrl', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://webapp.url.app/offres/NE?lieu=CU',
      },
      writable: true,
    })
  })

  describe('when offer with mediation', () => {
    it('should return webapp local offer URL when app is on development env', () => {
      // given
      config.IS_PROD = false
      const offerId = 'AN'
      const mediationId = 'AM'

      // when
      const discoveryUrl = webappOfferUrl(offerId, mediationId)

      // then
      expect(discoveryUrl).toBe('http://localhost:3000/offre/details/AN/AM')
    })

    it('should return webapp offer URL with same domain when app is on remote env', () => {
      // given
      config.IS_PROD = true
      const offerId = 'AN'
      const mediationId = 'AM'

      // when
      const discoveryUrl = webappOfferUrl(offerId, mediationId)

      // then
      expect(discoveryUrl).toBe('http://webapp.url.app/offre/details/AN/AM')
    })
  })

  describe('when offer without mediation', () => {
    it('should return webapp offer URL', () => {
      // given
      config.IS_PROD = true
      const offerId = 'AN'
      const mediationId = undefined

      // when
      const discoveryUrl = webappOfferUrl(offerId, mediationId)

      // then
      expect(discoveryUrl).toBe('http://webapp.url.app/offre/details/AN')
    })
  })
})

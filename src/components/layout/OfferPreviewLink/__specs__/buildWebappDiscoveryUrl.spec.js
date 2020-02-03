import { buildWebappDiscoveryUrl } from '../buildWebappDiscoveryUrl'
import * as config from '../../../../utils/config'


describe('src | components | pages | Offer | utils | buildWebappDiscoveryUrl', () => {
  beforeAll(() => {
    delete window.location
    Object.defineProperty(window, 'location', {
      writable: true,
    })
  })

  it('should return webapp URL in localhost on port 3000 when app is on development env', () => {
    // given
    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://webapp.url.com/offres/NE?lieu=CU',
      },
      writable: true,
    })
    config.IS_PROD = false

    const offerId = 'AN'
    const mediationId = 'AM'

    // when
    const discoveryUrl = buildWebappDiscoveryUrl(offerId, mediationId)

    // then
    expect(discoveryUrl).toStrictEqual('http://localhost:3000/offre/details/AN/AM')
  })

  it('should return webapp URL with same domain when app is on remote env', () => {
    // given
    Object.defineProperty(window, 'location', {
      value: {
        href: 'https://pro.passculture-test.beta.gouv.fr/offres/NE?lieu=CU',
      },
      writable: true,
    })
    config.IS_PROD = true

    const offerId = 'AN'
    const mediationId = 'AM'

    // when
    const discoveryUrl = buildWebappDiscoveryUrl(offerId, mediationId)

    // then
    expect(discoveryUrl).toStrictEqual('https://app.passculture-test.beta.gouv.fr/offre/details/AN/AM')
  })
})

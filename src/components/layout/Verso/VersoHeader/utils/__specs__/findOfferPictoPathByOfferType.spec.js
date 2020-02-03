import findOfferPictoPathByOfferType from '../findOfferPictoPathByOfferType'
import { ICONS_URL } from '../../../../../../utils/config'

jest.mock('../../../../../../utils/config', () => ({
  ICONS_URL: '/storage/picto/url'
}))

describe('src | components | layout | Verso | VersoHeader | utils | findOfferPictoPathByOfferType', () => {
  it('should return an url to the matching icon when offer type is provided', () => {
    // given
    const offerType = 'EventType.SPECTACLE_VIVANT'

    // when
    const result = findOfferPictoPathByOfferType(offerType)

    // then
    expect(result).toBe(`${ICONS_URL}/picto-spectacle.svg`)
  })

  it('should return an url to the eye icon when offer type is cinema card', () => {
    // given
    const offerType = 'ThingType.CINEMA_CARD'

    // when
    const result = findOfferPictoPathByOfferType(offerType)

    // then
    expect(result).toBe(`${ICONS_URL}/picto-visite.svg`)
  })

  it('should return null when offer type is null', () => {
    // given
    const offerType = null

    // when
    const result = findOfferPictoPathByOfferType(offerType)

    // then
    expect(result).toBeNull()
  })
})

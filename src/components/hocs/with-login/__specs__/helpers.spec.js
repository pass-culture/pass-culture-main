import {
  getRedirectToCurrentLocationOrTypeform,
  getRedirectToCurrentLocationOrDiscovery,
} from '../helpers'

describe('src | hocs | with-login | helpers', () => {
  describe('getRedirectToCurrentLocationOrTypeform', () => {
    it('should return undefined when user has filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: false,
        },
        pathname: '/my-page',
        search: '?any=any',
      }

      // then
      const result = getRedirectToCurrentLocationOrTypeform(props)

      // when
      expect(result).toBeUndefined()
    })

    it('should return typeform location when user has not filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: true,
        },
        pathname: '/my-page',
        search: '?any=any',
      }

      // then
      const result = getRedirectToCurrentLocationOrTypeform(props)

      // when
      expect(result).toStrictEqual('/typeform')
    })
  })

  describe('getRedirectToCurrentLocationOrDiscovery', () => {
    it('should return discovery location when user has filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: false,
        },
        pathname: '/my-page',
        search: '?any=any',
      }

      // then
      const result = getRedirectToCurrentLocationOrDiscovery(props)

      // when
      expect(result).toStrictEqual('/decouverte')
    })

    it('should return undefined when user has not filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: true,
        },
        pathname: '/my-page',
        search: '?any=any',
      }

      // then
      const result = getRedirectToCurrentLocationOrDiscovery(props)

      // when
      expect(result).toBeUndefined()
    })
  })
})

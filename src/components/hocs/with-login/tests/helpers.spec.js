import {
  getRedirectToCurrentLocationOrTypeform,
  getRedirectToDiscoveryOrTypeform,
} from '../helpers'

describe('src | hocs | with-login | helpers', () => {
  describe('getRedirectToDiscoveryOrTypeform', () => {
    it('should return current location when user has filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          hasFilledCulturalSurvey: true,
        },
        location: {
          pathname: '/my-page',
          search: '?any=any',
        },
      }

      // then
      const result = getRedirectToCurrentLocationOrTypeform(props)

      // when
      expect(result).toEqual('/my-page?any=any')
    })

    it('should return typeform location when user has not filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          hasFilledCulturalSurvey: false,
        },
        location: {
          pathname: '/my-page',
          search: '?any=any',
        },
      }

      // then
      const result = getRedirectToCurrentLocationOrTypeform(props)

      // when
      expect(result).toEqual('/typeform')
    })
  })
  describe('getRedirectToDiscoveryOrTypeform', () => {
    it('should return discovery location when user has filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          hasFilledCulturalSurvey: true,
        },
        location: {
          pathname: '/my-page',
          search: '?any=any',
        },
      }

      // then
      const result = getRedirectToDiscoveryOrTypeform(props)

      // when
      expect(result).toEqual('/decouverte')
    })

    it('should return typeform location when user has not filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          hasFilledCulturalSurvey: false,
        },
        location: {
          pathname: '/my-page',
          search: '?any=any',
        },
      }

      // then
      const result = getRedirectToDiscoveryOrTypeform(props)

      // when
      expect(result).toEqual('/typeform')
    })
  })
})

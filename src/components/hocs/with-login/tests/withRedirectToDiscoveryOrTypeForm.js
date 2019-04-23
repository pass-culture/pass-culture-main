import { getSuccessRedirection } from '../withRedirectToDiscoveryOrTypeForm'

describe('src | hocs | with-login | getSuccessRedirection', () => {
  describe('getSuccessRedirection', () => {
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
      const result = getSuccessRedirection(props)

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
      const result = getSuccessRedirection(props)

      // when
      expect(result).toEqual('/typeform')
    })
  })
})

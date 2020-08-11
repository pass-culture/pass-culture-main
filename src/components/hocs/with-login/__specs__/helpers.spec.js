import { getRedirectionPath, getRedirectToCurrentLocationOrDiscovery } from '../helpers'

describe('src | hocs | with-login | helpers', () => {
  describe('getRedirectionPath', () => {
    describe('when user has not filled the Typeform', () => {
      it('should return typeform location', () => {
        // given
        const props = {
          currentUser: {
            needsToFillCulturalSurvey: true,
          },
        }

        // then
        const result = getRedirectionPath(props)

        // when
        expect(result).toStrictEqual('/typeform')
      })
    })

    describe('when user has filled the Typeform', () => {
      describe('when user has not seen tutorials', () => {
        it('should return to tutorials', () => {
          // given
          const props = {
            currentUser: {
              needsToFillCulturalSurvey: false,
              needsToSeeTutorials: true,
            },
          }

          // then
          const result = getRedirectionPath(props)

          // when
          expect(result).toStrictEqual('/bienvenue')
        })
      })

      describe('when user has seen tutorials', () => {
        it('should return undefined', () => {
          // given
          const props = {
            currentUser: {
              needsToFillCulturalSurvey: false,
              needsToSeeTutorials: false,
            },
            pathname: '/my-page',
            search: '?any=any',
          }

          // then
          const result = getRedirectionPath(props)

          // when
          expect(result).toBeUndefined()
        })
      })
    })
  })

  describe('getRedirectToCurrentLocationOrDiscovery', () => {
    it('should return discovery location when user has filled the Typeform and homepage is disabled', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: false,
        },
        isHomepageDisabled: true
      }

      // then
      const result = getRedirectToCurrentLocationOrDiscovery(props)

      // when
      expect(result).toStrictEqual('/decouverte')
    })

    it('should return home location when user has filled the Typeform and homepage is enabled', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: false,
        },
        isHomepageDisabled: false
      }

      // then
      const result = getRedirectToCurrentLocationOrDiscovery(props)

      // when
      expect(result).toStrictEqual('/accueil')
    })

    it('should return undefined when user has not filled the Typeform', () => {
      // given
      const props = {
        currentUser: {
          needsToFillCulturalSurvey: true,
        },
      }

      // then
      const result = getRedirectToCurrentLocationOrDiscovery(props)

      // when
      expect(result).toBeUndefined()
    })
  })
})

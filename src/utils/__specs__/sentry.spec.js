import { configureCustomTags } from '../sentry'

describe('utils | Sentry', () => {
  describe('configureScope', () => {
    it('should add a custom tag', () => {
      // Given
      const scope = {
        setTag: jest.fn(),
      }

      // When
      configureCustomTags(scope)

      // Then
      expect(scope.setTag).toHaveBeenCalledWith('platform', 'browser')
    })

    it('should add a different value when coming from android application', () => {
      // Given
      /*document.referrer = 'android-app://app.passculture.testing.webapp'*/
      Object.defineProperty(document, 'referrer', {
        get: () => 'android-app://app.passculture.testing.webapp',
      })
      const scope = {
        setTag: jest.fn(),
      }

      // When
      configureCustomTags(scope)

      // Then
      expect(scope.setTag).toHaveBeenCalledWith('platform', 'application')
    })
  })
})

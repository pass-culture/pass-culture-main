import { configureCustomTags } from '../sentry'

jest.mock('../../utils/config', () => ({
  ANDROID_APPLICATION_ID: 'app.passculture.testing.webapp',
}))

describe('utils | Sentry', () => {
  describe('configureScope', () => {
    it('should set sentry tag when coming from browser', () => {
      // Given
      const scope = {
        setTag: jest.fn(),
      }

      // When
      configureCustomTags(scope)

      // Then
      expect(scope.setTag).toHaveBeenCalledWith('platform', 'browser')
    })

    it('should set sentry tag when coming from the configured android application', () => {
      // Given
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

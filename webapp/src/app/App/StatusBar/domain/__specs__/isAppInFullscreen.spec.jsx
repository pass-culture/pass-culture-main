/* eslint-disable jest/prefer-spy-on */
import { isAppInFullscreen } from '../isAppInFullscreen'

describe('isAppInFullscreen', () => {
  let originalWindow = window

  afterEach(() => {
    // eslint-disable-next-line no-global-assign
    window = originalWindow
  })

  describe('when on iOS device', () => {
    it('should return true if iOS app is in fullscreen', () => {
      // Given
      window.matchMedia = jest.fn().mockReturnValue({ matches: false })
      window.navigator.standalone = true

      // When
      const appInFullscreen = isAppInFullscreen()

      // Then
      expect(appInFullscreen).toBe(true)
    })

    it('should return false if not in fullscreen', () => {
      // Given
      window.matchMedia = jest.fn().mockReturnValue({ matches: false })
      window.navigator.standalone = false

      // When
      const appInFullscreen = isAppInFullscreen()

      // Then
      expect(appInFullscreen).toBe(false)
    })
  })

  describe('when on Android device', () => {
    it('should return true if Android app is in fullscreen', () => {
      // Given
      window.matchMedia = jest.fn().mockReturnValue({ matches: true })
      window.navigator.standalone = false

      // When
      const appInFullscreen = isAppInFullscreen()

      // Then
      expect(appInFullscreen).toBe(true)
      expect(window.matchMedia).toHaveBeenCalledWith('(display-mode: standalone)')
    })

    it('should return false if not in fullscreen', () => {
      // Given
      window.matchMedia = jest.fn().mockReturnValue({ matches: false })
      window.navigator.standalone = false

      // When
      const appInFullscreen = isAppInFullscreen()

      // Then
      expect(appInFullscreen).toBe(false)
    })
  })
})

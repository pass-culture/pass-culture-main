import { isFeatureDisabled } from '../featureFlipping'

describe('Config | Feature Flipping', () => {
  describe('isFeatureDisabled', () => {
    it('returns false if feature is unknown', () => {
      // Then
      const isActive = isFeatureDisabled('unknownFeature')
      // When
      expect(isActive).toEqual(true)
    })

    it('returns true if feature exists and value is true', () => {
      // Given
      global.features = { knownFeature: true }
      // Then
      const isActive = isFeatureDisabled('knownFeature')
      // When
      expect(isActive).toEqual(false)
    })

    it('returns true if feature exists and value is false', () => {
      // Given
      global.features = { nonActivatedFeature: false }
      // Then
      const isActive = isFeatureDisabled('nonActivatedFeature')
      // When
      expect(isActive).toEqual(true)
    })
  })
})

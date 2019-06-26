import isFeatureActive from "../featureFlipping";

describe('Config | Feature Flipping', () => {
  describe('isFeatureActive', () => {
    it('returns false if feature is unknown', () =>{
      // Then
      const isActive = isFeatureActive('unknownFeature')
      // When
      expect(isActive).toEqual(false)
    })

    it('returns true if feature exists and value is true', () =>{
      // Given
      global.features = {'knownFeature': true}
      // Then
      const isActive = isFeatureActive('knownFeature')
      // When
      expect(isActive).toEqual(true)
  })

    it('returns true if feature exists and value is false', () =>{
      // Given
      global.features = {'nonActivatedFeature': false}
      // Then
      const isActive = isFeatureActive('nonActivatedFeature')
      // When
      expect(isActive).toEqual(false)
    })
  })
})

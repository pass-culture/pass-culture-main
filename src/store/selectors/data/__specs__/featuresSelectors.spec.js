import { isAPISireneAvailable, selectIsFeatureActive } from '../featuresSelectors'

describe('selectors | features', () => {
  describe('selectIsFeatureActive', () => {
    it('should return true when features is Empty', () => {
      // when
      const state = { data: { features: [] } }
      const featureName = null

      // when
      const isFeatureActive = selectIsFeatureActive(state, featureName)

      // then
      expect(isFeatureActive).toStrictEqual(false)
    })

    it('should return true when featureName is falsy', () => {
      // when
      const state = { data: { features: [{ nameKey: 'FOO' }] } }
      const featureName = null

      // when
      const isFeatureActive = selectIsFeatureActive(state, featureName)

      // then
      expect(isFeatureActive).toStrictEqual(false)
    })

    it('should return true when selected feature is not found', () => {
      // when
      const state = { data: { features: [{ nameKey: 'FOO' }] } }
      const featureName = 'BAR'

      // when
      const isFeatureActive = selectIsFeatureActive(state, featureName)

      // then
      expect(isFeatureActive).toStrictEqual(false)
    })

    it('should return true when selected feature is not active', () => {
      // when
      const state = { data: { features: [{ isActive: false, nameKey: 'FOO' }] } }
      const featureName = 'FOO'

      // when
      const isFeatureActive = selectIsFeatureActive(state, featureName)

      // then
      expect(isFeatureActive).toStrictEqual(false)
    })
  })

  describe('isAPISireneAvailable', () => {
    describe('when the API_SIRENE_AVAILABLE feature is disabled', () => {
      it('should return false', () => {
        // given
        const state = {
          data: {
            features: [
              {
                isActive: false,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = isAPISireneAvailable(state)

        // then
        expect(result).toStrictEqual(false)
      })
    })

    describe('when the API_SIRENE_AVAILABLE feature is activated', () => {
      it('should return true', () => {
        // given
        const state = {
          data: {
            features: [
              {
                isActive: true,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = isAPISireneAvailable(state)

        // then
        expect(result).toStrictEqual(true)
      })
    })
  })
})

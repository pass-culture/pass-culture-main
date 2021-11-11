import { mapStateToProps } from '../EligibilityCheckContainer'

describe('eligibility check container', () => {
  describe('mapStateToProps()', () => {
    it('should map feature flags', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              name: 'ALLOW_IDCHECK_REGISTRATION',
              nameKey: 'ALLOW_IDCHECK_REGISTRATION',
            },
          ],
        },
        features: {
          fetchHasFailed: false,
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isIdCheckAvailable: true,
        wholeFranceOpening: true,
      })
    })

    it('should ignore other features', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              name: 'PLACEHOLDER',
              nameKey: 'PLACEHOLDER',
            },
            {
              isActive: false,
              name: 'ALLOW_IDCHECK_REGISTRATION',
              nameKey: 'ALLOW_IDCHECK_REGISTRATION',
            },
          ],
        },
        features: {
          fetchHasFailed: false,
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isIdCheckAvailable: false,
        wholeFranceOpening: true,
      })
    })
  })
  describe('mapStateToProps() when fetch has failed', () => {
    it('should map feature flags', () => {
      const state = {
        data: {
          features: [],
        },
        features: {
          fetchHasFailed: true,
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isIdCheckAvailable: false,
        wholeFranceOpening: true,
      })
    })
  })
})

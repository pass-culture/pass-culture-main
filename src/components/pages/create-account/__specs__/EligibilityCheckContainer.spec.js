import { mapStateToProps } from '../EligibilityCheckContainer'

describe('eligibility check container', () => {
  describe('mapStateToProps()', () => {
    it('should the map the id check status', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              name: 'APPLY_BOOKING_LIMITS_V2',
              nameKey: 'APPLY_BOOKING_LIMITS_V2',
            },
            {
              isActive: true,
              name: 'ALLOW_IDCHECK_REGISTRATION',
              nameKey: 'ALLOW_IDCHECK_REGISTRATION',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isIdCheckAvailable: true,
      })
    })

    it('should ignore other features', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              name: 'APPLY_BOOKING_LIMITS_V2',
              nameKey: 'APPLY_BOOKING_LIMITS_V2',
            },
            {
              isActive: false,
              name: 'ALLOW_IDCHECK_REGISTRATION',
              nameKey: 'ALLOW_IDCHECK_REGISTRATION',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isIdCheckAvailable: false,
      })
    })
  })
})

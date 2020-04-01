import { mapStateToProps } from '../DiscoveryRouterContainer'

describe('discoveryRouterContainer', () => {
  describe('when discovery v2 feature flipping is active', () => {
    it('should load discovery v2', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              nameKey: 'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isDiscoveryV2Active: true,
      })
    })
  })

  describe('when discovery v2 feature flipping is deactive', () => {
    it('should load discovery v1', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: false,
              nameKey: 'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isDiscoveryV2Active: false,
      })
    })
  })
})

import { mapStateToProps } from '../OffererItemContainer'

describe('src | components | pages | Offerers | OffererItem | OffererItemContainer', () => {
  describe('mapStateToProps', () => {
    describe('isVenueCreationAvailable is based on feature flipping', () => {
      it('should mark offerer creation possible when API sirene is available', () => {
        // given
        const state = {
          features: {
            list: [
              {
                isActive: true,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state)

        // then
        expect(result).toHaveProperty('isVenueCreationAvailable', true)
      })

      it('should prevent offerer creation when feature API sirene is not available', () => {
        // given
        const state = {
          features: {
            list: [
              {
                isActive: false,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state)

        // then
        expect(result).toHaveProperty('isVenueCreationAvailable', false)
      })
    })
  })
})

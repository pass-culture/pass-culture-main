import { mapStateToProps } from '../OfferersContainer'

describe('src | components | pages | Offerers | OfferersContainer', () => {
  describe('mapStateToProps', () => {
    describe('isOffererCreationAvailable is based on feature flipping', () => {
      it('should mark offerer creation possible when API sirene is available', () => {
        // given
        const props = {}
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
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isOffererCreationAvailable', true)
      })

      it('should prevent offerer creation when feature API sirene is not available', () => {
        // given
        const props = {}
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
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isOffererCreationAvailable', false)
      })
    })
  })
})

import { mapStateToProps } from '../SigninContainer'

describe('pages | Signin | SigninContainer', () => {
  describe('when the API_SIRENE_AVAILABLE feature is disabled', () => {
    it('should mark account creation as disabled', () => {
      // given
      const state = {
        data: {},
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
      const props = mapStateToProps(state)

      // then
      expect(props).toHaveProperty('isAccountCreationAvailable', false)
    })
  })

  describe('when the API_SIRENE_AVAILABLE feature is activated', () => {
    it('should mark account creation as disabled', () => {
      // given
      const state = {
        data: {},
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
      const props = mapStateToProps(state)

      // then
      expect(props).toHaveProperty('isAccountCreationAvailable', true)
    })
  })
})

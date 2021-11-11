import { mergeProps, mapStateToProps } from '../TutorialsContainer'
import { FEATURES } from '../../../router/selectors/features'

describe('src | components | pages | tutorials | TutorialsContainer', () => {
  describe('mapStateToProps', () => {
    describe('userHasNewDepositVersion', () => {
      it("is activated when user's deposit is v2", () => {
        // given
        const state = {
          currentUser: {
            deposit_version: 2,
          },
          data: {
            features: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('userHasNewDepositVersion', true)
      })

      it("is disabled when user's deposit is 1", () => {
        // given
        const state = {
          currentUser: {
            deposit_version: 1,
          },
          data: {
            features: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('userHasNewDepositVersion', false)
      })

      it('is activated when user has no deposit', () => {
        // given
        const state = {
          currentUser: {
            deposit_version: null,
          },
          data: {
            features: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('userHasNewDepositVersion', true)
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let updateCurrentUser

    beforeEach(() => {
      updateCurrentUser = jest.fn()
    })

    describe('saveUserHasSeenTutorials', () => {
      it('should dispatch an action with the right parameters and redirect to decouverte when homepage feature is inactive', async () => {
        // given
        const isHomepageDisabled = true
        const history = {
          push: jest.fn(),
        }
        // when
        await mergeProps(
          {
            data: {
              features: [
                {
                  nameKey: FEATURES.HOMEPAGE,
                  isActive: false,
                },
              ],
            },
          },
          { updateCurrentUser },
          { history }
        ).saveUserHasSeenTutorials(isHomepageDisabled)

        // then
        expect(updateCurrentUser).toHaveBeenCalledWith({
          hasSeenTutorials: true,
        })
        expect(history.push).toHaveBeenCalledWith('/decouverte')
      })

      it('should dispatch an action with the right parameters and redirect to accueil when homepage feature is active', async () => {
        // given
        const isHomepageDisabled = false
        const history = {
          push: jest.fn(),
        }
        // when
        await mergeProps(
          {
            data: {
              features: [
                {
                  nameKey: FEATURES.HOMEPAGE,
                  isActive: true,
                },
              ],
            },
          },
          { updateCurrentUser },
          { history }
        ).saveUserHasSeenTutorials(isHomepageDisabled)

        // then
        expect(updateCurrentUser).toHaveBeenCalledWith({
          hasSeenTutorials: true,
        })
        expect(history.push).toHaveBeenCalledWith('/accueil')
      })
    })
  })
})

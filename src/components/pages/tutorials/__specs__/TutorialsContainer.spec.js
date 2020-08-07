import { mergeProps } from '../TutorialsContainer'
import { FEATURES } from '../../../router/selectors/features'

describe('src | components | pages | tutorials | TutorialsContainer', () => {
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
        await mergeProps({
          data: {
            features: [{
              nameKey: FEATURES.HOMEPAGE,
              isActive: false,
            }],
          },
        }, { updateCurrentUser }, { history }).saveUserHasSeenTutorials(isHomepageDisabled)

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
        await mergeProps({
          data: {
            features: [{
              nameKey: FEATURES.HOMEPAGE,
              isActive: true,
            }],
          },
        }, { updateCurrentUser }, { history }).saveUserHasSeenTutorials(isHomepageDisabled)

        // then
        expect(updateCurrentUser).toHaveBeenCalledWith({
          hasSeenTutorials: true,
        })
        expect(history.push).toHaveBeenCalledWith('/accueil')
      })
    })
  })
})

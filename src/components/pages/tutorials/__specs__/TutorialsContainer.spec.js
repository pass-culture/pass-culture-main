import { mergeProps } from '../TutorialsContainer'

describe('src | components | pages | tutorials | TutorialsContainer', () => {
  describe('mapDispatchToProps', () => {
    let updateCurrentUser

    beforeEach(() => {
      updateCurrentUser = jest.fn()
    })

    describe('saveUserHasSeenTutorials', () => {
      it('should dispatch an action with the right parameters', () => {
        // when
        mergeProps(undefined, { updateCurrentUser }, { history }).saveUserHasSeenTutorials()

        // then
        expect(updateCurrentUser).toHaveBeenCalledWith({
          hasSeenTutorials: true,
        })
      })
    })
  })
})

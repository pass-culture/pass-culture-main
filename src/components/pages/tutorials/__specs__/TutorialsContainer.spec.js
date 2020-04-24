import { mapDispatchToProps } from '../TutorialsContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
  }
})

describe('src | components | pages | tutorials | TutorialsContainer', () => {
  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('saveUserHasSeenTutorials', () => {
      it('should dispatch an action with the right parameters', () => {
        // when
        mapDispatchToProps(dispatch).saveUserHasSeenTutorials()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/users/current',
            body: {
              hasSeenTutorials: true,
            },
            method: 'PATCH',
          },
          type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
        })
      })
    })
  })
})

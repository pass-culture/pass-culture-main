import { handleFail, handleSuccess } from '../withRequiredLogin'
import { getRedirectToSignin, getRedirectToCurrentLocationOrTypeform } from '../helpers'

jest.mock('../helpers')

describe('src | components | pages | hocs | with-login | withRequiredLogin - unit tests', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('handleFail()', () => {
    it('should call push history when it fails', () => {
      // given
      const state = {}
      const action = {}
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToSignin.mockReturnValue('/fake-url')

      // when
      handleFail(state, action, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrTypeform with right parameters', () => {
      // given
      const state = {}
      const action = {
        payload: {
          datum: {
            email: 'michel.marx@youpi.fr',
            needsToFillCulturalSurvey: false,
          },
        },
      }

      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {
          hash: '',
          key: expect.any(String),
          pathname: '/test',
          search: '',
          state: undefined,
        },
      }

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(getRedirectToCurrentLocationOrTypeform).toHaveBeenCalledWith({
        currentUser: {
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: false,
        },
        hash: '',
        key: expect.any(String),
        pathname: '/test',
        search: '',
        state: undefined,
      })
    })

    it('should call push history when user is redirected', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrTypeform.mockReturnValue('/fake-url')

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })

    it('should not call push history when successful', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrTypeform.mockReturnValue(undefined)

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).not.toHaveBeenCalled()
    })
  })
})

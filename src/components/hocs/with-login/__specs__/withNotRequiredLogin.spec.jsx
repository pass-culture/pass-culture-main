import { handleSuccess } from '../withNotRequiredLogin'
import { getRedirectToCurrentLocationOrDiscovery } from '../helpers'

jest.mock('../helpers')

describe('src | components | pages | hocs | with-login | withNotRequiredLogin', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrDiscovery with right parameters', () => {
      // given
      const user = {
        email: 'michel.marx@youpi.fr',
        needsToFillCulturalSurvey: false,
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
      handleSuccess(user, ownProps)

      // then
      expect(getRedirectToCurrentLocationOrDiscovery).toHaveBeenCalledWith({
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

    it('should not call push history when user is redirected', () => {
      // given
      const user = null
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue('/fake-url')

      // when
      handleSuccess(user, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })

    it('should call push history when its success', () => {
      // given
      const user = null
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue(undefined)

      // when
      handleSuccess(user, ownProps)

      // then
      expect(ownProps.history.push).not.toHaveBeenCalled()
    })
  })
})

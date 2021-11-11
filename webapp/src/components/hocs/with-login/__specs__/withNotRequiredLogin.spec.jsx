import { handleSuccess } from '../withNotRequiredLogin'
import { getRedirectToCurrentLocationOrDiscoveryOrHome } from '../helpers'

jest.mock('../helpers')

describe('src | components | pages | hocs | with-login | withNotRequiredLogin', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrDiscoveryOrHome with right parameters', () => {
      // given
      const user = {
        email: 'michel.marx@youpi.fr',
        needsToFillCulturalSurvey: false,
      }
      const history = {
        push: jest.fn(),
      }
      const location = {
        hash: '',
        key: expect.any(String),
        pathname: '/test',
        search: '',
        state: undefined,
      }

      // when
      handleSuccess({
        currentUser: user,
        isHomepageDisabled: true,
        history: history,
        location: location,
      })

      // then
      expect(getRedirectToCurrentLocationOrDiscoveryOrHome).toHaveBeenCalledWith({
        currentUser: {
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: false,
        },
        hash: '',
        isHomepageDisabled: true,
        key: expect.any(String),
        pathname: '/test',
        search: '',
        state: undefined,
      })
    })

    it('should call push history when user is redirected', () => {
      // given
      const user = null
      const history = {
        push: jest.fn(),
      }
      const location = {}
      getRedirectToCurrentLocationOrDiscoveryOrHome.mockReturnValue('/fake-url')

      // when
      handleSuccess({
        currentUser: user,
        history: history,
        location: location,
      })

      // then
      expect(history.push).toHaveBeenCalledWith('/fake-url')
    })

    it('should not call push history when user is not redirected', () => {
      // given
      const user = null
      const history = {
        push: jest.fn(),
      }
      const location = {}
      getRedirectToCurrentLocationOrDiscoveryOrHome.mockReturnValue(undefined)

      // when
      handleSuccess({
        currentUser: user,
        history: history,
        location: location
      })

      // then
      expect(history.push).not.toHaveBeenCalled()
    })
  })
})

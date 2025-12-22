import { render } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import type {
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
} from '@/apiClient/v1'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { useRouterGuard } from '../useRouterGuard'

const navigateMock = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  Navigate: ({ to }: { to: string }) => {
    navigateMock(to)
    return null
  },
}))
vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))

const RouterGuardTestComponent = () => {
  const redirection = useRouterGuard()

  return redirection
}

const renderUseRouterGuard = ({
  initialRoute,
  currentUser,
  access,
  selectedVenue,
  features = [],
}: {
  initialRoute: string
  currentUser: SharedCurrentUserResponseModel | null
  access: UserAccess | null
  selectedVenue: GetVenueResponseModel | null
  features?: string[]
}) => {
  const featuresList = features.map((feature, index) => ({
    id: index,
    isActive: true,
    name: feature,
  }))
  const store = configureTestStore({
    user: { currentUser, access, selectedVenue, venues: null },
    features: { list: featuresList },
  })

  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <RouterGuardTestComponent />
      </MemoryRouter>
    </Provider>
  )
}

describe('useRouterGuard()', () => {
  beforeEach(() => {
    navigateMock.mockClear()
  })

  describe('without WIP_SWITCH_VENUE feature flag', () => {
    it('should return null regardless of user state', () => {
      renderUseRouterGuard({
        initialRoute: '/accueil',
        currentUser: null,
        access: null,
        selectedVenue: null,
        features: [],
      })

      expect(navigateMock).not.toHaveBeenCalled()
    })
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    describe('when user is not authenticated', () => {
      it('should redirect to Login when accessing private route /accueil', () => {
        renderUseRouterGuard({
          initialRoute: '/accueil',
          currentUser: null,
          access: null,
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).toHaveBeenCalledWith('/connexion')
      })

      it('should not redirect when accessing public route /connexion', () => {
        renderUseRouterGuard({
          initialRoute: '/connexion',
          currentUser: null,
          access: null,
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })

      it('should not redirect when accessing permissionless route /accessibilite', () => {
        renderUseRouterGuard({
          initialRoute: '/accessibilite',
          currentUser: null,
          access: null,
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })
    })

    describe('when user is authenticated without selected venue', () => {
      it('should redirect to Hub when accessing /accueil', () => {
        renderUseRouterGuard({
          initialRoute: '/accueil',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).toHaveBeenCalledWith('/hub')
      })

      it('should not redirect when already on /hub', () => {
        renderUseRouterGuard({
          initialRoute: '/hub',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })

      it('should redirect to Hub when accessing /connexion (public route forbidding authenticated)', () => {
        renderUseRouterGuard({
          initialRoute: '/connexion',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: null,
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).toHaveBeenCalledWith('/hub')
      })
    })

    describe('when user has unattached access with selected venue', () => {
      it('should redirect to PendingVenueAssociation when accessing /accueil', () => {
        renderUseRouterGuard({
          initialRoute: '/accueil',
          currentUser: sharedCurrentUserFactory(),
          access: 'unattached',
          selectedVenue: makeGetVenueResponseModel({ id: 1 }),
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).toHaveBeenCalledWith('/rattachement-en-cours')
      })

      it('should not redirect when already on /rattachement-en-cours', () => {
        renderUseRouterGuard({
          initialRoute: '/rattachement-en-cours',
          currentUser: sharedCurrentUserFactory(),
          access: 'unattached',
          selectedVenue: makeGetVenueResponseModel({ id: 1 }),
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })
    })

    describe('when user has full access with selected venue', () => {
      it('should not redirect when accessing /accueil', () => {
        renderUseRouterGuard({
          initialRoute: '/accueil',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: makeGetVenueResponseModel({ id: 1 }),
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })

      it('should redirect to Homepage when accessing /connexion', () => {
        renderUseRouterGuard({
          initialRoute: '/connexion',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: makeGetVenueResponseModel({ id: 1 }),
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).toHaveBeenCalledWith('/accueil')
      })

      it('should not redirect when accessing permissionless route /accessibilite', () => {
        renderUseRouterGuard({
          initialRoute: '/accessibilite',
          currentUser: sharedCurrentUserFactory(),
          access: 'full',
          selectedVenue: makeGetVenueResponseModel({ id: 1 }),
          features: ['WIP_SWITCH_VENUE'],
        })

        expect(navigateMock).not.toHaveBeenCalled()
      })
    })
  })
})

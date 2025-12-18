import { screen } from '@testing-library/react'
import * as react_router from 'react-router'

import { AppRouterGuard } from '@/app/AppRouter/AppRouterGuard'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  Navigate: () => vi.fn(),
}))

const renderGuard = ({
  access,
  initialRoute = '/',
  user = sharedCurrentUserFactory(),
  features = [],
  selectedVenue,
}: Partial<{
  access: UserAccess | null
  initialRoute: string
  user: ReturnType<typeof sharedCurrentUserFactory> | null
  features: string[]
  selectedVenue: ReturnType<typeof makeGetVenueResponseModel> | null
}>) =>
  renderWithProviders(
    <AppRouterGuard>
      <></>
    </AppRouterGuard>,
    {
      initialRouterEntries: [initialRoute],
      user,
      features,
      storeOverrides: {
        user: {
          currentUser: user,
          access,
          selectedVenue,
        },
      },
    }
  )

describe('AppRouterGuard', () => {
  beforeEach(() => {
    // Mock Navigate behavior to check if the right route is called.
    // @ts-expect-error
    vi.spyOn(react_router, 'Navigate').mockImplementation((props) => (
      <h1>{props.to.toString()}</h1>
    ))
  })

  it('should redirect to login if not logged in on a private page', () => {
    renderGuard({})

    expect(screen.getByText('/connexion')).toBeInTheDocument()
  })

  it('should redirect to logged page if user access public page', () => {
    renderGuard({ access: 'full', initialRoute: '/connexion' })

    expect(screen.getByText(/accueil/)).toBeInTheDocument()
  })

  it('should redirect to onboarding journey if user just subscribed', () => {
    renderGuard({ access: 'no-offerer', initialRoute: '/accueil' })

    expect(
      screen.getByText('/inscription/structure/recherche')
    ).toBeInTheDocument()
  })

  it('should redirect to unattached page if user is not attached', () => {
    renderGuard({ access: 'unattached', initialRoute: '/accueil' })

    expect(screen.getByText('/rattachement-en-cours')).toBeInTheDocument()
  })

  it('should redirect onboarding if user is not onboarded', () => {
    renderGuard({ access: 'no-onboarding', initialRoute: '/accueil' })

    expect(screen.getByText('/onboarding')).toBeInTheDocument()
  })

  it('should not redirect if user is not onboarded and tries to create an offerer', () => {
    renderGuard({
      access: 'no-onboarding',
      initialRoute: '/inscription/structure/recherche',
    })

    expect(screen.queryByText('/onboarding')).not.toBeInTheDocument()
  })

  it('should redirect to home if user is onboarded and access onboarding pages', () => {
    renderGuard({ access: 'full', initialRoute: '/onboarding' })

    expect(screen.getByText('/accueil')).toBeInTheDocument()
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    it('should redirect to Hub when logged in without selected venue while on a private route', () => {
      renderGuard({
        user: sharedCurrentUserFactory(),
        features: ['WIP_SWITCH_VENUE'],
        initialRoute: '/accueil',
        selectedVenue: null,
      })

      expect(screen.getByText('/hub')).toBeInTheDocument()
    })

    it('should not redirect when logged in without selected venue while already on Hub route', () => {
      renderGuard({
        user: sharedCurrentUserFactory(),
        features: ['WIP_SWITCH_VENUE'],
        initialRoute: '/hub',
        selectedVenue: null,
      })

      expect(screen.queryByText('/hub')).not.toBeInTheDocument()
      expect(screen.queryByText('/connexion')).not.toBeInTheDocument()
    })

    it('should not redirect when logged in with selected venue', () => {
      renderGuard({
        user: sharedCurrentUserFactory(),
        features: ['WIP_SWITCH_VENUE'],
        initialRoute: '/accueil',
        selectedVenue: makeGetVenueResponseModel({ id: 1 }),
      })

      expect(screen.queryByText('/hub')).not.toBeInTheDocument()
      expect(screen.queryByText('/connexion')).not.toBeInTheDocument()
    })

    it('should redirect to Login when not logged in while on a private route', () => {
      renderGuard({
        user: null,
        features: ['WIP_SWITCH_VENUE'],
        initialRoute: '/accueil',
      })

      expect(screen.getByText('/connexion')).toBeInTheDocument()
    })

    it('should not redirect when not logged in while on a public route', () => {
      renderGuard({
        user: null,
        features: ['WIP_SWITCH_VENUE'],
        initialRoute: '/connexion',
      })

      expect(screen.queryByText('/connexion')).not.toBeInTheDocument()
      expect(screen.queryByText('/hub')).not.toBeInTheDocument()
    })
  })
})

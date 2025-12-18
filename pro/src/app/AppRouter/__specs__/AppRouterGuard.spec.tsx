import { screen } from '@testing-library/react'
import * as react_router from 'react-router'

import { AppRouterGuard } from '@/app/AppRouter/AppRouterGuard'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  Navigate: () => vi.fn(),
}))

const renderGuard = (
  access?: UserAccess | null,
  initialRoute: string = '/',
  user = sharedCurrentUserFactory()
) =>
  renderWithProviders(
    <AppRouterGuard>
      <></>
    </AppRouterGuard>,
    {
      initialRouterEntries: [initialRoute],
      user,
      storeOverrides: {
        user: {
          currentUser: user,
          access,
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
    renderGuard()

    expect(screen.getByText('/connexion')).toBeInTheDocument()
  })

  it('should redirect to logged page if user access public page', () => {
    renderGuard('full', '/connexion')

    expect(screen.getByText(/accueil/)).toBeInTheDocument()
  })

  it('should redirect to onboarding journey if user just subscribed', () => {
    renderGuard('no-offerer', '/accueil')

    expect(
      screen.getByText('/inscription/structure/recherche')
    ).toBeInTheDocument()
  })

  it('should redirect to unattached page if user is not attached', () => {
    renderGuard('unattached', '/accueil')

    expect(screen.getByText('/rattachement-en-cours')).toBeInTheDocument()
  })

  it('should redirect onboarding if user is not onboarded', () => {
    renderGuard('no-onboarding', '/accueil')

    expect(screen.getByText('/onboarding')).toBeInTheDocument()
  })

  it('should not redirect if user is not onboarded and tries to create an offerer', () => {
    renderGuard('no-onboarding', '/inscription/structure/recherche')

    expect(screen.queryByText('/onboarding')).not.toBeInTheDocument()
  })

  it('should redirect to home if user is onboarded and access onboarding pages', () => {
    renderGuard('full', '/onboarding')

    expect(screen.getByText('/accueil')).toBeInTheDocument()
  })
})

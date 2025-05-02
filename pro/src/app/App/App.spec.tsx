import { setUser } from '@sentry/browser'
import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import * as orejime from 'app/App/analytics/orejime'
import { App } from 'app/App/App'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import * as useHasAccessToDidacticOnboarding from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { RootState } from 'commons/store/rootReducer'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

vi.mock('app/App/analytics/firebase', () => ({ useFirebase: vi.fn() }))
vi.mock('app/App/hook/useLogNavigation', () => ({ useLogNavigation: vi.fn() }))
vi.mock('app/App/hook/useLogExtraProData', () => ({
  useLogExtraProData: vi.fn(),
}))
vi.mock('app/App/hook/usePageTitle', () => ({ usePageTitle: vi.fn() }))
vi.mock('@sentry/browser', () => ({ setUser: vi.fn() }))

function TestBrokenCallComponent() {
  useSWR([GET_OFFER_QUERY_KEY], () => api.getOffer(17))

  return <>broken page</>
}

const renderApp = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <>
      <div id="root" />

      <Routes>
        <Route path="/" element={<App />}>
          <Route path="/" element={<p>Sub component</p>} />
          <Route path="/adage-iframe" element={<p>ADAGE</p>} />
          <Route path="/offres" element={<p>Offres</p>} />
          <Route path="/connexion" element={<p>Login page</p>} />
          <Route
            path="/parcours-inscription"
            element={<p>Onboarding page</p>}
          />
          <Route path="/broken-page" element={<TestBrokenCallComponent />} />
          <Route path="/404" element={<p>404 page</p>} />
          <Route path="/accueil" element={<p>accueil</p>} />
          <Route path="/onboarding" element={<p>onboarding didactique</p>} />
        </Route>
      </Routes>
    </>,
    {
      initialRouterEntries: ['/'],
      user: sharedCurrentUserFactory(),
      ...options,
    }
  )

global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: {
    href: 'someurl',
  },
  writable: true,
})
vi.mock('commons/hooks/useHasAccessToDidacticOnboarding')

describe('App', () => {
  beforeEach(() => {
    vi.spyOn(window, 'scrollTo')
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])

    vi.spyOn(
      useHasAccessToDidacticOnboarding,
      'useHasAccessToDidacticOnboarding'
    ).mockResolvedValue(true)
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    const user = sharedCurrentUserFactory({ hasUserOfferer: true })
    renderApp({ user })

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({
      id: user.id.toString(),
    })
  })

  it('should redirect to login if not logged in on a private page', async () => {
    renderApp({ initialRouterEntries: ['/offres'], user: undefined })

    expect(await screen.findByText('Login page')).toBeInTheDocument()
  })

  it('should redirect to onboarding if has no user_offerer on private page', async () => {
    renderApp({
      user: sharedCurrentUserFactory({ hasUserOfferer: false }),
      initialRouterEntries: ['/offres'],
    })

    expect(await screen.findByText('Onboarding page')).toBeInTheDocument()
  })

  it('should not initialize firebase on the adage iframe', async () => {
    vi.spyOn(orejime, 'useOrejime').mockImplementation(() => ({
      consentedToBeamer: false,
      consentedToFirebase: false,
    }))

    const useAnalyticsSpy = vi
      .spyOn(useAnalytics, 'useFirebase')
      .mockImplementation(() => {})

    renderApp({ initialRouterEntries: ['/adage-iframe'] })

    await screen.findByText('ADAGE')

    expect(useAnalyticsSpy).not.toHaveBeenCalledWith(
      expect.objectContaining({ isCookieEnabled: true })
    )
  })

  it('should redirect to page 404 when api has not found', async () => {
    vi.spyOn(api, 'getOffer').mockRejectedValueOnce({
      status: 404,
      name: 'ApiError',
      message: 'oh no',
    })
    const user = sharedCurrentUserFactory({ hasUserOfferer: true })

    renderApp({
      initialRouterEntries: ['/broken-page'],
      user,
    })

    expect(await screen.findByText('broken page')).toBeInTheDocument()

    expect(await screen.findByText('404 page')).toBeInTheDocument()
  })

  describe('Onboarding status', () => {
    const user = sharedCurrentUserFactory({ hasUserOfferer: true })
    const overrides: Partial<RootState> = {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory({ isOnboarded: false }),
    }

    it('should redirect to onboarding if user is not onboarded and tries to go to home page', async () => {
      renderApp({
        initialRouterEntries: ['/accueil'],
        storeOverrides: overrides,
        user,
        features: ['WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'],
      })

      expect(
        await screen.findByText('onboarding didactique')
      ).toBeInTheDocument()
    })

    it('should not redirect if user is not onboarded and tries to go to offers', async () => {
      renderApp({
        initialRouterEntries: ['/offres'],
        storeOverrides: overrides,
        user,
        features: ['WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'],
      })

      expect(await screen.findByText('Offres')).toBeInTheDocument()
    })

    it('should redirect to home if user is onboarded and tries to go to onboarding', async () => {
      renderApp({
        initialRouterEntries: ['/onboarding'],
        storeOverrides: {
          ...overrides,
          offerer: {
            selectedOffererId: 1,
            offererNames: [],
            isOnboarded: true,
          },
        },
        features: ['WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'],
        user,
      })

      expect(await screen.findByText('accueil')).toBeInTheDocument()
    })
  })
})

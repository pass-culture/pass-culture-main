import { setUser } from '@sentry/browser'
import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { App } from '@/app/App/App'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as orejime from '@/app/App/analytics/orejime'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

vi.mock('@/app/App/analytics/firebase', () => ({ useFirebase: vi.fn() }))
vi.mock('@/app/App/hook/useLogNavigation', () => ({
  useLogNavigation: vi.fn(),
}))
vi.mock('@/app/App/hook/useLogExtraProData', () => ({
  useLogExtraProData: vi.fn(),
}))
vi.mock('@/app/App/hook/usePageTitle', () => ({ usePageTitle: vi.fn() }))
vi.mock('@sentry/browser', () => ({ setUser: vi.fn() }))

function TestBrokenCallComponent() {
  useSWR([GET_OFFER_QUERY_KEY], () => api.getOffer(17))

  return 'broken page'
}

const renderApp = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <>
      <div id={'root'} />

      <Routes>
        <Route path="/" element={<App />}>
          <Route path="/" element={<p>Sub component</p>} />
          <Route path="/adage-iframe" element={<p>ADAGE</p>} />
          <Route path="/offres" element={<p>Offres</p>} />
          <Route path="/connexion" element={<p>Login page</p>} />
          <Route
            path="/inscription/structure/recherche"
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

const user = sharedCurrentUserFactory({ hasUserOfferer: true })

describe('App', () => {
  beforeEach(() => {
    vi.spyOn(window, 'scrollTo')
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    renderApp({ user })

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({
      id: user.id.toString(),
    })
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
})

describe('App – load offerer via from-bo', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(
      defaultGetOffererResponseModel
    )
  })

  it('should call api.getOfferer when user come from back-office (?from-bo=...&structure=ID)', async () => {
    renderApp({
      initialRouterEntries: ['/?from-bo=true&structure=123'],
      user,
    })

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
      expect(api.getOfferer).toHaveBeenCalledWith(123)
    })
  })

  it('should not call api.getOfferer if user do not come form back-office (from-bo)', () => {
    renderApp({
      initialRouterEntries: ['/?from-bo=false&structure=null'],
      user,
    })

    expect(api.getOfferer).not.toHaveBeenCalled()
  })
})

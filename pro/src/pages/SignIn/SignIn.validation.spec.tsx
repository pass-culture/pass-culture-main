import { screen } from '@testing-library/react'
import * as router from 'react-router'
import { Route, Routes } from 'react-router'

import { apiNew } from '@/apiClient/api'
import type { SharedLoginUserResponseModel } from '@/apiClient/v1'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import * as utils from '@/commons/utils/recaptcha'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { SignIn } from './SignIn'

vi.mock('@/apiClient/api', () => ({
  api: {
    signin: vi.fn(),
  },
  apiNew: {
    getOfferer: vi.fn(),
    listOfferersNames: vi.fn(),
    getProfile: vi.fn(),
  },
}))

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useSearchParams: () => [],
}))

const renderSignIn = (options?: RenderWithProvidersOptions) => {
  renderWithProviders(
    <>
      <SignIn />
      <Routes>
        <Route
          path="/accueil"
          element={<span>I’m logged standard user redirect route</span>}
        />
        <Route
          path="/inscription"
          element={<span>I’m the inscription page</span>}
        />
        <Route
          path="/inscription/structure/recherche"
          element={<span>I’m the onboarding page</span>}
        />
        <Route path="/offres" element={<span>I’m the offer page</span>} />
      </Routes>
      <SnackBarContainer />
    </>,
    {
      initialRouterEntries: ['/connexion'],
      features: ['API_SIRENE_AVAILABLE'],
      ...options,
    }
  )
}
const scrollIntoViewMock = vi.fn()
describe('SignIn', () => {
  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    vi.spyOn(apiNew, 'getProfile').mockResolvedValue(sharedCurrentUserFactory())
    vi.spyOn(apiNew, 'signin').mockResolvedValue(
      {} as SharedLoginUserResponseModel
    )
    vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
      remove: vi.fn(),
    } as unknown as HTMLScriptElement)
    vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Mon super cinéma',
          validated: true,
        }),
        getOffererNameFactory({
          id: 1,
          name: 'Ma super librairie',
          validated: true,
        }),
      ],
    })

    vi.spyOn(apiNew, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
  })

  describe('should display messages after account validation', () => {
    it('should display confirmation', async () => {
      vi.spyOn(router, 'useSearchParams').mockReturnValue([
        new URLSearchParams({ accountValidation: 'true' }),
        vi.fn(),
      ])
      renderSignIn()
      expect(
        await screen.findByText(
          'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
        )
      ).toBeInTheDocument()
    })

    it('should display error', async () => {
      vi.spyOn(router, 'useSearchParams').mockReturnValue([
        new URLSearchParams({
          accountValidation: 'false',
          message: 'Erreur invalide',
        }),
        vi.fn(),
      ])
      renderSignIn()
      expect(await screen.findByText('Erreur invalide')).toBeInTheDocument()
    })
  })
})

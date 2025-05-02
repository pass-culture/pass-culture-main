import { screen } from '@testing-library/react'
import * as router from 'react-router'
import { Route, Routes } from 'react-router'

import { api } from 'apiClient/api'
import { SharedLoginUserResponseModel } from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import * as utils from 'commons/utils/recaptcha'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import { SignIn } from './SignIn'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    signin: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

vi.mock('commons/utils/windowMatchMedia', () => ({
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
          path="/parcours-inscription"
          element={<span>I’m the onboarding page</span>}
        />
        <Route path="/offres" element={<span>I’m the offer page</span>} />
      </Routes>
      <Notification />
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
    vi.spyOn(api, 'getProfile').mockResolvedValue(sharedCurrentUserFactory())
    vi.spyOn(api, 'signin').mockResolvedValue(
      {} as SharedLoginUserResponseModel
    )
    vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
      remove: vi.fn(),
    } as unknown as HTMLScriptElement)
    vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Mon super cinéma',
        }),
        getOffererNameFactory({
          id: 1,
          name: 'Ma super librairie',
        }),
      ],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(
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

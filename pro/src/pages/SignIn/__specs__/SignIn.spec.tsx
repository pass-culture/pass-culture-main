import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { ApiError, SharedLoginUserResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import { getOffererNameFactory } from 'utils/individualApiFactories'
import * as utils from 'utils/recaptcha'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SignIn } from '../SignIn'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    signin: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

const mockLogEvent = vi.fn()

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
  })

  it('should display 2 inputs and one link to account creation and one button to login', () => {
    // When
    renderSignIn()

    // Then
    expect(screen.getByLabelText('Adresse email *')).toBeInTheDocument()
    expect(screen.getByLabelText('Mot de passe *')).toBeInTheDocument()
    expect(screen.getByText('Se connecter')).toBeInTheDocument()
    expect(screen.getByText('Créer un compte')).toBeInTheDocument()
    expect(screen.getByText('Mot de passe oublié ?')).toBeInTheDocument()
    expect(
      screen.getByText('Consulter nos recommandations de sécurité')
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-'
    )
  })

  describe('when user clicks on the eye on password input', () => {
    it('should reveal password', async () => {
      // When
      renderSignIn()
      const eyePasswordButton = screen.getByRole('button', {
        name: 'Afficher le mot de passe',
      })

      // Then
      await userEvent.click(eyePasswordButton)

      expect(screen.getByLabelText('Mot de passe *')).toHaveAttribute(
        'type',
        'text'
      )
    })

    it('should hide password when user re-click on eye', async () => {
      // Given
      renderSignIn()
      const eyePasswordButton = screen.getByRole('button', {
        name: 'Afficher le mot de passe',
      })

      // When
      await userEvent.click(eyePasswordButton)
      await userEvent.click(eyePasswordButton)

      //then
      expect(screen.getByLabelText('Mot de passe *')).toHaveAttribute(
        'type',
        'password'
      )
    })
  })

  describe("when user clicks on 'Créer un compte'", () => {
    it('should redirect to the creation page when the API sirene is available', () => {
      renderSignIn()

      expect(
        screen.getByRole('link', { name: 'Créer un compte' })
      ).toHaveAttribute('href', '/inscription')
    })

    it('should redirect to the unavailable error page when the API sirene feature is disabled', () => {
      renderSignIn({ features: [] })

      // then
      expect(
        screen.getByRole('link', { name: 'Créer un compte' })
      ).toHaveAttribute('href', '/erreur/indisponible')
    })

    it('should trigger a tracking event', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      renderSignIn()
      await userEvent.click(
        screen.getByRole('link', {
          name: 'Créer un compte',
        })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_CREATE_ACCOUNT,
        { from: '/connexion' }
      )
    })
  })

  it('should call submit prop when user clicks on "Se connecter"', async () => {
    renderSignIn()

    const email = screen.getByLabelText('Adresse email *')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe *')
    await userEvent.type(password, 'MCSolar85')
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Se connecter',
      })
    )
    expect(api.signin).toHaveBeenCalledWith({
      identifier: 'MonPetitEmail@exemple.com',
      password: 'MCSolar85',
      captchaToken: 'token',
    })
  })

  describe('when user is signed in', () => {
    it('should redirect to offerers page if user is not admin', async () => {
      renderSignIn({ user: sharedCurrentUserFactory() })

      await waitFor(() =>
        expect(
          screen.getByText('I’m logged standard user redirect route')
        ).toBeInTheDocument()
      )
    })
  })

  it('should display errors message and focus email input when login failed', async () => {
    renderSignIn()

    const email = screen.getByLabelText('Adresse email *')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe *')
    await userEvent.type(password, 'MCSolar85')

    vi.spyOn(api, 'signin').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          url: '',
          body: { identifier: ['password is invalid'] },
          status: 401,
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Se connecter',
      })
    )

    expect(
      screen.getAllByText('Identifiant ou mot de passe incorrect.')
    ).toHaveLength(3)

    expect(screen.getByLabelText('Adresse email *')).toHaveFocus()
  })

  it('should display an error message when login rate limit exceeded', async () => {
    renderSignIn()

    const email = screen.getByLabelText('Adresse email *')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe *')
    await userEvent.type(password, 'MCSolar85')

    vi.spyOn(api, 'signin').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          url: '',
          body: {
            identifier: [
              'Nombre de tentatives de connexion dépassé, veuillez réessayer dans une minute',
            ],
          },
          status: HTTP_STATUS.TOO_MANY_REQUESTS,
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Se connecter',
      })
    )

    expect(
      await screen.findByText(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    ).toBeInTheDocument()
  })

  describe('sign in with new onboarding feature', () => {
    it('should not call listOfferersNames if user is admin', () => {
      const listOfferersNamesRequest = vi.spyOn(api, 'listOfferersNames')

      renderSignIn({ user: sharedCurrentUserFactory({ isAdmin: true }) })

      expect(listOfferersNamesRequest).toHaveBeenCalledTimes(0)
    })

    it('should redirect to onboarding page if offerer list is empty', async () => {
      const listOfferersNamesRequest = vi
        .spyOn(api, 'listOfferersNames')
        .mockResolvedValueOnce({
          offerersNames: [],
        })

      renderSignIn()

      const email = screen.getByLabelText('Adresse email *')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe *')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(listOfferersNamesRequest).toHaveBeenCalledTimes(1)
      expect(screen.getByText('I’m the onboarding page')).toBeInTheDocument()
    })

    it('should not redirect user to onboarding page if use has an offerer', async () => {
      renderSignIn()

      const email = screen.getByLabelText('Adresse email *')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe *')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(
        screen.getByText('I’m logged standard user redirect route')
      ).toBeInTheDocument()
    })

    it('should redirect user to offer page on signin with url parameter', async () => {
      renderSignIn({ initialRouterEntries: ['/connexion?de=%2Foffres'] })

      const email = screen.getByLabelText('Adresse email *')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe *')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(screen.getByText('I’m the offer page')).toBeInTheDocument()
    })
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

  describe('tracking', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
    })

    it('should trigger a tracking event', async () => {
      renderSignIn()
      await userEvent.click(
        screen.getByRole('link', {
          name: 'Créer un compte',
        })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_CREATE_ACCOUNT,
        { from: '/connexion' }
      )
    })

    it('should trigger a tracking event when user clicks forgotten password"', async () => {
      renderSignIn()

      await userEvent.click(
        screen.getByRole('link', {
          name: 'Mot de passe oublié ?',
        })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_FORGOTTEN_PASSWORD,
        { from: '/connexion' }
      )
    })
  })
})

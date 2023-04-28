import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import {
  ApiError,
  SharedCurrentUserResponseModel,
  SharedLoginUserResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignIn from '../SignIn'

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    signin: jest.fn(),
    listOfferersNames: jest.fn(),
  },
}))

const mockLogEvent = jest.fn()

const renderSignIn = (
  storeOverrides?: any,
  initialRouterEntries = ['/connexion']
) => {
  const store = {
    user: {},
    app: {},
    features: {
      list: [
        {
          isActive: true,
          nameKey: 'API_SIRENE_AVAILABLE',
        },
      ],
    },
    ...storeOverrides,
  }
  renderWithProviders(
    <>
      <SignIn />
      <Routes>
        <Route
          path="/accueil"
          element={<span>I'm logged standard user redirect route</span>}
        />
        <Route
          path="/inscription"
          element={<span>I'm the inscription page</span>}
        />
        <Route
          path="/parcours-inscription"
          element={<span>I'm the onboarding page</span>}
        />
        <Route path="/offres" element={<span>I'm the offer page</span>} />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides: store,
      initialRouterEntries: initialRouterEntries,
    }
  )
}

describe('src | components | pages | SignIn', () => {
  beforeEach(() => {
    jest
      .spyOn(api, 'getProfile')
      .mockResolvedValue({} as SharedCurrentUserResponseModel)
    jest
      .spyOn(api, 'signin')
      .mockResolvedValue({} as SharedLoginUserResponseModel)
  })

  it('should display 2 inputs and one link to account creation and one button to login', () => {
    // When
    renderSignIn()

    // Then
    expect(screen.getByLabelText('Adresse e-mail')).toBeInTheDocument()
    expect(screen.getByLabelText('Mot de passe')).toBeInTheDocument()
    expect(screen.getByText('Se connecter')).toBeInTheDocument()
    expect(screen.getByText('Créer un compte')).toBeInTheDocument()
    expect(screen.getByText('Mot de passe oublié ?')).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: 'Consulter nos recommandations de sécurité',
      })
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

      expect(await screen.getByLabelText('Mot de passe')).toHaveAttribute(
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
      expect(await screen.getByLabelText('Mot de passe')).toHaveAttribute(
        'type',
        'password'
      )
    })
  })

  describe("when user clicks on 'Créer un compte'", () => {
    it('should redirect to the creation page when the API sirene is available', () => {
      // when
      renderSignIn()

      // then
      expect(
        screen.getByRole('link', { name: 'Créer un compte' })
      ).toHaveAttribute('href', '/inscription')
    })

    it('should redirect to the unavailable error page when the API sirene feature is disabled', async () => {
      renderSignIn({
        features: {
          list: [
            {
              isActive: false,
              nameKey: 'API_SIRENE_AVAILABLE',
            },
          ],
        },
      })

      // then
      expect(
        screen.getByRole('link', { name: 'Créer un compte' })
      ).toHaveAttribute('href', '/erreur/indisponible')
    })

    it('should trigger a tracking event', async () => {
      jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
        setLogEvent: null,
      }))

      renderSignIn({ user: { initialized: true, currentUser: null } })
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

    const email = screen.getByLabelText('Adresse e-mail')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe')
    await userEvent.type(password, 'MCSolar85')
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Se connecter',
      })
    )
    expect(api.signin).toHaveBeenCalledWith({
      identifier: 'MonPetitEmail@exemple.com',
      password: 'MCSolar85',
    })
  })

  describe('when user is signed in', () => {
    it('should redirect to offerers page if user is not admin', async () => {
      renderSignIn({
        user: {
          currentUser: {
            id: 'user_id',
            isAdmin: false,
          },
          initialized: true,
        },
      })
      expect(
        screen.getByText("I'm logged standard user redirect route")
      ).toBeInTheDocument()
    })
  })

  it('should display an error message when login failed', async () => {
    renderSignIn()

    const email = screen.getByLabelText('Adresse e-mail')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe')
    await userEvent.type(password, 'MCSolar85')

    jest.spyOn(api, 'signin').mockRejectedValueOnce(
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
      await screen.findByText('Identifiant ou mot de passe incorrect.')
    ).toBeInTheDocument()
  })

  it('should display an error message when login rate limit exceeded', async () => {
    renderSignIn()

    const email = screen.getByLabelText('Adresse e-mail')
    await userEvent.type(email, 'MonPetitEmail@exemple.com')
    const password = screen.getByLabelText('Mot de passe')
    await userEvent.type(password, 'MCSolar85')

    jest.spyOn(api, 'signin').mockRejectedValueOnce(
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
    const featureOverride = {
      features: {
        list: [
          {
            isActive: true,
            nameKey: 'API_SIRENE_AVAILABLE',
          },
          { nameKey: 'WIP_ENABLE_NEW_ONBOARDING', isActive: true },
        ],
      },
    }

    it('should not call listOfferersNames if user is admin', async () => {
      const listOfferersNamesRequest = jest
        .spyOn(api, 'listOfferersNames')
        .mockResolvedValue({
          offerersNames: [
            {
              id: 'A1',
              nonHumanizedId: 1,
              name: 'Mon super cinéma',
            },
            {
              id: 'B1',
              nonHumanizedId: 1,
              name: 'Ma super librairie',
            },
          ],
        })

      renderSignIn({
        user: {
          currentUser: {
            id: 'user_id',
            isAdmin: true,
          },
          initialized: true,
        },
        ...featureOverride,
      })

      expect(listOfferersNamesRequest).toHaveBeenCalledTimes(0)
    })

    it('should redirect to onboarding page if offerer list is empty', async () => {
      const listOfferersNamesRequest = jest
        .spyOn(api, 'listOfferersNames')
        .mockResolvedValue({
          offerersNames: [],
        })

      renderSignIn({ ...featureOverride })

      const email = screen.getByLabelText('Adresse e-mail')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(listOfferersNamesRequest).toHaveBeenCalledTimes(1)
      expect(screen.getByText("I'm the onboarding page")).toBeInTheDocument()
    })

    it('should not redirect user to onboarding page if use has an offerer', async () => {
      jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          {
            id: 'A1',
            nonHumanizedId: 1,
            name: 'Mon super cinéma',
          },
          {
            id: 'B1',
            nonHumanizedId: 1,
            name: 'Ma super librairie',
          },
        ],
      })

      renderSignIn({ ...featureOverride })

      const email = screen.getByLabelText('Adresse e-mail')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(
        screen.getByText("I'm logged standard user redirect route")
      ).toBeInTheDocument()
    })

    it('should redirect user to offer page on signin with url parameter', async () => {
      jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          {
            id: 'A1',
            nonHumanizedId: 1,
            name: 'Mon super cinéma',
          },
          {
            id: 'B1',
            nonHumanizedId: 1,
            name: 'Ma super librairie',
          },
        ],
      })

      renderSignIn({ ...featureOverride }, ['/connexion?de=%2Foffres'])

      const email = screen.getByLabelText('Adresse e-mail')
      await userEvent.type(email, 'MonPetitEmail@exemple.com')

      const password = screen.getByLabelText('Mot de passe')
      await userEvent.type(password, 'MCSolar85')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Se connecter',
        })
      )

      expect(screen.getByText("I'm the offer page")).toBeInTheDocument()
    })
  })
})

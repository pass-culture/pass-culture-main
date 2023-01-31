import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route } from 'react-router'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignIn from '../SignIn'

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    signin: jest.fn(),
  },
}))

const renderSignIn = storeOverrides =>
  renderWithProviders(
    <>
      <SignIn />
      <Route path="/accueil">
        <span>I'm logged standard user redirect route</span>
      </Route>
      <Route path="/structures">
        <span>I'm logged admin redirect route</span>
      </Route>
      <Route path="/inscription">
        <span>I'm the inscription page</span>
      </Route>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: ['/connexion'] }
  )

describe('src | components | pages | SignIn', () => {
  let store
  beforeEach(() => {
    store = {
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
    }

    jest.spyOn(api, 'getProfile').mockResolvedValue({})
    jest.spyOn(api, 'signin').mockResolvedValue({})
  })

  it('should display 2 inputs and one link to account creation and one button to login', () => {
    // When
    renderSignIn(store)

    // Then
    expect(screen.getByLabelText('Adresse e-mail')).toBeInTheDocument()
    expect(screen.getByLabelText('Mot de passe')).toBeInTheDocument()
    expect(screen.getByText('Se connecter')).toBeInTheDocument()
    expect(screen.getByText('Créer un compte')).toBeInTheDocument()
    expect(screen.getByText('Mot de passe égaré ?')).toBeInTheDocument()
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
      renderSignIn(store)
      const eyePasswordButton = screen.getByRole('button', {
        name: 'Afficher le mot de passe',
      })

      // Then
      await userEvent.click(eyePasswordButton)

      const password = screen.getByLabelText('Mot de passe')
      expect(password.type).toBe('text')
    })

    describe('when user re-click on eye', () => {
      it('should hide password', async () => {
        // Given
        renderSignIn(store)
        const eyePasswordButton = screen.getByRole('button', {
          name: 'Afficher le mot de passe',
        })

        // When
        await userEvent.click(eyePasswordButton)
        await userEvent.click(eyePasswordButton)

        //then
        const password = screen.getByLabelText('Mot de passe')
        expect(password.type).toBe('password')
      })
    })
    describe("when user clicks on 'Créer un compte'", () => {
      describe('when the API sirene is available', () => {
        it('should redirect to the creation page', () => {
          // when
          renderSignIn(store)

          // then
          expect(
            screen.getByRole('link', { name: 'Créer un compte' })
          ).toHaveAttribute('href', '/inscription')
        })
      })
      describe('when the API sirene feature is disabled', () => {
        it('should redirect to the unavailable error page', () => {
          store.features.list = [
            {
              isActive: false,
              nameKey: 'API_SIRENE_AVAILABLE',
            },
          ]
          renderSignIn(store)

          // then
          expect(
            screen.getByRole('link', { name: 'Créer un compte' })
          ).toHaveAttribute('href', '/erreur/indisponible')
        })
      })
      it('should trigger a tracking event', async () => {
        const mockLogEvent = jest.fn()
        jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
          logEvent: mockLogEvent,
        }))
        store.user = { initialized: true, currentUser: null }
        renderSignIn(store)
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
  })
  describe('when user clicks on "Se connecter"', () => {
    it('should call submit prop', async () => {
      renderSignIn(store)

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
      it('should redirect to homepage if user is admin', async () => {
        store.user = {
          currentUser: {
            id: 'user_id',
            publicName: 'François',
            isAdmin: true,
          },
          initialized: true,
        }

        renderSignIn(store)
        expect(
          screen.getByText("I'm logged admin redirect route")
        ).toBeInTheDocument()
      })
      it('should redirect to offerers page if user is not admin', async () => {
        store.user = {
          currentUser: {
            id: 'user_id',
            publicName: 'François',
            isAdmin: false,
          },
          initialized: true,
        }

        renderSignIn(store)
        expect(
          screen.getByText("I'm logged standard user redirect route")
        ).toBeInTheDocument()
      })
    })

    describe('when login failed', () => {
      it('should display an error message', async () => {
        renderSignIn(store)

        const email = screen.getByLabelText('Adresse e-mail')
        await userEvent.type(email, 'MonPetitEmail@exemple.com')
        const password = screen.getByLabelText('Mot de passe')
        await userEvent.type(password, 'MCSolar85')

        api.signin.mockRejectedValue(
          new ApiError(
            {},
            {
              url: '',
              body: { identifier: ['password is invalid'] },
              status: 401,
            }
          )
        )
        await userEvent.click(
          screen.getByRole('button', {
            name: 'Se connecter',
          })
        )

        expect(
          screen.getByText('Identifiant ou mot de passe incorrect.')
        ).toBeInTheDocument()
      })
    })

    describe('when login rate limit exceeded', () => {
      it('should display an error message', async () => {
        renderSignIn(store)

        const email = screen.getByLabelText('Adresse e-mail')
        await userEvent.type(email, 'MonPetitEmail@exemple.com')
        const password = screen.getByLabelText('Mot de passe')
        await userEvent.type(password, 'MCSolar85')

        api.signin.mockRejectedValue(
          new ApiError(
            {},
            {
              url: '',
              errors: {
                global:
                  'Nombre de tentatives de connexion dépassé, veuillez réessayer dans une minute',
              },
              status: HTTP_STATUS.TOO_MANY_REQUESTS,
            }
          )
        )
        await userEvent.click(
          screen.getByRole('button', {
            name: 'Se connecter',
          })
        )

        expect(
          screen.getByText(
            'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
          )
        ).toBeInTheDocument()
      })
    })
  })
})

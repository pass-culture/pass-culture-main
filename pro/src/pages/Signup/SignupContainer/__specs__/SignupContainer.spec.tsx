import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { getOffererNameFactory } from 'utils/individualApiFactories'
import * as utils from 'utils/recaptcha'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SignupContainer } from '../SignupContainer'

const mockLogEvent = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({}),
    signupProV2: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))

const renderSignUp = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <Routes>
      <Route path="/inscription" element={<SignupContainer />} />
      <Route
        path="/accueil"
        element={<span>I’m logged in as a pro user</span>}
      />
      <Route
        path="/inscription/confirmation"
        element={<span>I’m the confirmation page</span>}
      />
    </Routes>,
    {
      initialRouterEntries: ['/inscription'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
      ...options,
    }
  )

describe('Signup', () => {
  beforeEach(() => {
    vi.spyOn(api, 'signupProV2').mockResolvedValue()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

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
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('should redirect to accueil page if the user is logged in', async () => {
    renderSignUp({ user: sharedCurrentUserFactory() })
    await expect(
      screen.findByText('I’m logged in as a pro user')
    ).resolves.toBeInTheDocument()
  })

  describe('render', () => {
    it('should render with all information', () => {
      // when the user sees the form
      renderSignUp()

      // then it should have a title
      expect(
        screen.getByRole('heading', {
          name: /Créer votre compte/,
        })
      ).toBeInTheDocument()
      // and an external link to the help center
      expect(
        screen.getByRole('link', {
          name: /Consulter notre centre d’aide/,
        })
      ).toHaveAttribute(
        'href',
        'https://passculture.zendesk.com/hc/fr/articles/4411999179665'
      )
      // and an external link to CGU
      expect(
        screen.getByRole('link', {
          name: /Conditions Générales d’Utilisation/,
        })
      ).toHaveAttribute('href', 'https://pass.culture.fr/cgu-professionnels/')
      // and an external link to GDPR chart
      expect(
        screen.getAllByRole('link', {
          name: /Charte des Données Personnelles/,
        })[0]
      ).toHaveAttribute('href', 'https://pass.culture.fr/donnees-personnelles/')
      // and a mail to support
      expect(
        screen.getByRole('link', {
          name: /Contacter notre support/,
        })
      ).toHaveAttribute('href', 'mailto:support-pro@passculture.app')

      // and a RGS link
      expect(
        screen.getByRole('link', {
          name: /Consulter nos recommandations de sécurité/,
        })
      ).toHaveAttribute(
        'href',
        'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-'
      )
      // and a link to signin page
      expect(
        screen.getByRole('button', {
          name: /J’ai déjà un compte/,
        })
      ).toBeInTheDocument()
    })

    it('should render with all fields', () => {
      // when the user sees the form
      renderSignUp()

      // then it should have an email field
      expect(
        screen.getByRole('textbox', {
          name: /Adresse email */,
        })
      ).toBeInTheDocument()
      // and a password field
      expect(screen.getByLabelText(/Mot de passe/)).toBeInTheDocument()
      // and a last name field
      expect(
        screen.getByRole('textbox', {
          name: /Nom/,
        })
      ).toBeInTheDocument()
      // and a first name field
      expect(
        screen.getByRole('textbox', {
          name: /Prénom/,
        })
      ).toBeInTheDocument()
      // and a telephone field
      expect(screen.getByLabelText('Numéro de téléphone')).toBeInTheDocument()
      // and a contact field
      expect(
        screen.getByRole('checkbox', {
          name: /pour recevoir les nouveautés du pass Culture et contribuer à son amélioration/,
        })
      ).toBeInTheDocument()
      // and a submit button
      expect(
        screen.getByRole('button', {
          name: /Créer mon compte/,
        })
      ).toBeInTheDocument()
    })

    describe('formlogEvents', () => {
      describe('on component unmount', () => {
        it('should trigger an event with touched fields', async () => {
          const { unmount } = renderSignUp()

          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          await userEvent.type(
            screen.getByLabelText('Numéro de téléphone'),
            '1234'
          )
          // We simulate onBlur to have email field touched
          await userEvent.tab()

          unmount()
          expect(mockLogEvent).toHaveBeenCalledTimes(1)
          expect(mockLogEvent).toHaveBeenNthCalledWith(
            1,
            Events.SIGNUP_FORM_ABORT,
            {
              filled: ['email', 'phoneNumber'],
              filledWithErrors: ['phoneNumber'],
            }
          )
        })
        it('should not trigger an event if no field has been touched', () => {
          const { unmount } = renderSignUp()
          unmount()
          expect(mockLogEvent).toHaveBeenCalledTimes(0)
        })
      })

      it('should have an beforeunload event listener attached to the window', () => {
        const spyAddEvent = vi.fn()
        const spyRemoveEvent = vi.fn()
        window.addEventListener = spyAddEvent
        window.removeEventListener = spyRemoveEvent

        const { unmount } = renderSignUp()
        // Count calls to window.addEventListener with "beforeunload" as first argument
        expect(
          spyAddEvent.mock.calls
            .map((args) => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(1)
        expect(
          spyRemoveEvent.mock.calls
            .map((args) => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(0)
        unmount()
        expect(
          spyRemoveEvent.mock.calls
            .map((args) => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(1)
      })
    })
    describe('formValidation', () => {
      describe('formValidation', () => {
        it('should enable submit button', async () => {
          vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
            remove: vi.fn(),
          } as unknown as HTMLScriptElement)
          vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
          renderSignUp({ features: ['ENABLE_PRO_ACCOUNT_CREATION'] })
          const submitButton = screen.getByRole('button', {
            name: /Créer mon compte/,
          })
          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          await userEvent.type(
            screen.getByLabelText(/Mot de passe/),
            'user@AZERTY123'
          )
          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Nom/,
            }),
            'Nom'
          )
          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Prénom/,
            }),
            'Prénom'
          )
          await userEvent.type(
            screen.getByLabelText('Numéro de téléphone'),
            '+33722332233'
          )
          expect(submitButton).toBeEnabled()

          // To simulate onBlur event
          await userEvent.tab()

          expect(submitButton).toBeEnabled()
          await userEvent.click(submitButton)

          expect(api.signupProV2).toHaveBeenCalledWith({
            contactOk: false,
            email: 'test@example.com',
            firstName: 'Prénom',
            lastName: 'Nom',
            password: 'user@AZERTY123', // NOSONAR
            phoneNumber: '+33722332233',
            token: 'token',
          })
          await expect(
            screen.findByText('I’m the confirmation page')
          ).resolves.toBeInTheDocument()
          expect(mockLogEvent).toHaveBeenNthCalledWith(
            1,
            Events.SIGNUP_FORM_SUCCESS,
            {}
          )
          expect(mockLogEvent).toHaveBeenCalledTimes(1)
        })
      })

      it('should show a notification on api call error', async () => {
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        vi.spyOn(api, 'signupProV2').mockRejectedValue({
          body: {
            phoneNumber: 'Le téléphone doit faire moins de 20 caractères',
          },
          status: HTTP_STATUS.GONE,
        })
        renderSignUp()

        const submitButton = screen.getByRole('button', {
          name: /Créer mon compte/,
        })

        await userEvent.type(
          screen.getByLabelText('Adresse email *'),
          'test@example.com'
        )
        await userEvent.type(
          screen.getByLabelText('Mot de passe *'),
          'user@AZERTY123'
        )
        await userEvent.type(screen.getByLabelText('Nom *'), 'Nom')
        await userEvent.type(screen.getByLabelText('Prénom *'), 'Prénom')

        await userEvent.type(
          screen.getByLabelText('Numéro de téléphone'),
          '0722332200'
        )
        // To simulate onBlur event
        await userEvent.tab()

        await userEvent.click(submitButton)
        expect(api.signupProV2).toHaveBeenCalledTimes(1)

        expect(
          await screen.findByText(
            'Le téléphone doit faire moins de 20 caractères'
          )
        ).toBeInTheDocument()

        const phoneInput = screen.getByLabelText('Numéro de téléphone')
        await userEvent.clear(phoneInput)
        await userEvent.type(phoneInput, '0622332233')
        await userEvent.tab()
        await waitFor(() => expect(submitButton).toBeEnabled())
      })
    })
  })
})

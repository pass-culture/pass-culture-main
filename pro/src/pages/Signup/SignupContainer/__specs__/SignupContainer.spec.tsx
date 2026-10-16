import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { HTTP_STATUS } from '@/apiClient/helpers'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import * as utils from '@/commons/utils/recaptcha'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { ApiError } from 'apiClient/compat'
import { SignupContainer } from '../SignupContainer'

const mockLogEvent = vi.fn()

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({}),
    signupPro: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))

const renderSignUp = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <Routes>
      <Route
        path="/inscription/compte/creation"
        element={<SignupContainer />}
      />
      <Route
        path="/accueil"
        element={<span>I’m logged in as a pro user</span>}
      />
      <Route
        path="/inscription/compte/confirmation"
        element={<span>I’m the confirmation page</span>}
      />
    </Routes>,
    {
      initialRouterEntries: ['/inscription/compte/creation'],
      ...options,
    }
  )

describe('Signup', () => {
  beforeEach(() => {
    vi.spyOn(api, 'signupPro').mockResolvedValue()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
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
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderSignUp()

    expect(await axe(container)).toHaveNoViolations()
  })

  describe('render', () => {
    it('should render with all information', () => {
      renderSignUp()

      expect(
        screen.getByRole('heading', { name: 'Créez votre compte' })
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          'Ces informations vous permettront de vous connecter à pass Culture Pro.'
        )
      ).toBeInTheDocument()

      expect(screen.getByRole('link', { name: 'Retour' })).toBeInTheDocument()

      expect(
        screen.getByRole('button', { name: 'Continuer' })
      ).toBeInTheDocument()

      expect(
        screen.getByRole('link', {
          name: /Conditions générales d’utilisation/,
        })
      ).toHaveAttribute('href', 'https://pass.culture.fr/cgu-professionnels/')
      expect(
        screen.getByRole('link', {
          name: /Se connecter/,
        })
      ).toBeInTheDocument()
    })

    it('should render with all fields', () => {
      renderSignUp()

      expect(
        screen.getByRole('textbox', {
          name: /Adresse email */,
        })
      ).toBeInTheDocument()
      expect(screen.getByLabelText(/Mot de passe/)).toBeInTheDocument()
      expect(
        screen.getByRole('textbox', {
          name: /Nom/,
        })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('textbox', {
          name: /Prénom/,
        })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('checkbox', {
          name: /pour recevoir les nouveautés du pass Culture et contribuer à son amélioration/,
        })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Continuer' })
      ).toBeInTheDocument()
    })

    describe('formlogEvents', () => {
      describe('on component unmount', () => {
        it('should trigger an event with touched fields', async () => {
          const user = userEvent.setup()
          const { unmount } = renderSignUp()

          await user.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          // We simulate onBlur to have email field touched
          await user.tab()
          await user.tab()

          unmount()
          await waitFor(() => {
            expect(mockLogEvent).toHaveBeenCalledTimes(1)
            expect(mockLogEvent).toHaveBeenNthCalledWith(
              1,
              Events.SIGNUP_FORM_ABORT,
              {
                filled: ['email', 'password'],
                filledWithErrors: ['password'],
              }
            )
          })
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
            .filter(Boolean)
        ).toHaveLength(1)
        expect(
          spyRemoveEvent.mock.calls
            .map((args) => args[0] === 'beforeunload')
            .filter(Boolean)
        ).toHaveLength(0)
        unmount()
        expect(
          spyRemoveEvent.mock.calls
            .map((args) => args[0] === 'beforeunload')
            .filter(Boolean)
        ).toHaveLength(1)
      })
    })
    describe('formValidation', () => {
      describe('formValidation', () => {
        it('should enable submit button', async () => {
          const user = userEvent.setup()
          vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
            remove: vi.fn(),
          } as unknown as HTMLScriptElement)
          vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
          renderSignUp({ features: ['ENABLE_PRO_ACCOUNT_CREATION'] })
          await user.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          await user.type(
            screen.getByLabelText(/Mot de passe/),
            'user@AZERTY123'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Nom/,
            }),
            'Nom'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Prénom/,
            }),
            'Prénom'
          )
          const submitButton = screen.getByRole('button', { name: 'Continuer' })
          expect(submitButton).toBeEnabled()

          // To simulate onBlur event
          await user.tab()

          expect(submitButton).toBeEnabled()

          await user.click(submitButton)

          expect(api.signupPro).toHaveBeenCalledWith({
            body: {
              contactOk: false,
              email: 'test@example.com',
              firstName: 'Prénom',
              lastName: 'Nom',
              password: 'user@AZERTY123', // NOSONAR
              structureSimulationInfos: null,
              token: 'token',
            },
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

        it('should enable submit button without phone number', async () => {
          const user = userEvent.setup()
          vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
            remove: vi.fn(),
          } as unknown as HTMLScriptElement)
          vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
          renderSignUp({
            features: ['ENABLE_PRO_ACCOUNT_CREATION'],
          })
          await user.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          await user.type(
            screen.getByLabelText(/Mot de passe/),
            'user@AZERTY123'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Nom/,
            }),
            'Nom'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Prénom/,
            }),
            'Prénom'
          )
          await user.tab()

          const submitButton = screen.getByRole('button', { name: 'Continuer' })
          expect(submitButton).toBeEnabled()
          await user.click(submitButton)

          expect(api.signupPro).toHaveBeenCalledWith({
            body: {
              contactOk: false,
              email: 'test@example.com',
              firstName: 'Prénom',
              lastName: 'Nom',
              password: 'user@AZERTY123', // NOSONAR
              structureSimulationInfos: null,
              token: 'token',
            },
          })
          await expect(
            screen.findByText('I’m the confirmation page')
          ).resolves.toBeInTheDocument()
        })

        it('should pass through the simulation information when given in the searchParams', async () => {
          const user = userEvent.setup()
          vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
            remove: vi.fn(),
          } as unknown as HTMLScriptElement)
          vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
          renderSignUp({
            initialRouterEntries: [
              '/inscription/compte/creation?isOpenToPublic=true&activity=RECORD_STORE&siret=11111111000011&targets=INDIVIDUAL&targets=COLLECTIVE',
            ],
          })

          await user.type(
            screen.getByRole('textbox', {
              name: /Adresse email */,
            }),
            'test@example.com'
          )
          await user.type(
            screen.getByLabelText(/Mot de passe/),
            'user@AZERTY123'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Nom/,
            }),
            'Nom'
          )
          await user.type(
            screen.getByRole('textbox', {
              name: /Prénom/,
            }),
            'Prénom'
          )
          await user.tab()

          const submitButton = screen.getByRole('button', { name: 'Continuer' })
          expect(submitButton).toBeEnabled()
          await user.click(submitButton)

          expect(api.signupPro).toHaveBeenCalledWith({
            body: {
              contactOk: false,
              email: 'test@example.com',
              firstName: 'Prénom',
              lastName: 'Nom',
              password: 'user@AZERTY123', // NOSONAR
              structureSimulationInfos: {
                activity: 'RECORD_STORE',
                isOpenToPublic: true,
                siret: '11111111000011',
                targets: ['INDIVIDUAL', 'COLLECTIVE'],
              },
              token: 'token',
            },
          })
          await expect(
            screen.findByText('I’m the confirmation page')
          ).resolves.toBeInTheDocument()
        })
      })

      it('should show a notification on api call error', async () => {
        const user = userEvent.setup()
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        vi.spyOn(api, 'signupPro').mockRejectedValue(
          new ApiError(
            {
              method: 'GET',
              url: 'https://noop',
            },
            {
              body: {
                phoneNumber: 'Le téléphone doit faire moins de 20 caractères',
              },
              status: HTTP_STATUS.GONE,
              statusText: 'Bad Request',
              url: 'https://noop',
              ok: false,
            },
            ''
          )
        )
        renderSignUp()

        await user.type(
          screen.getByLabelText(/Adresse email/),
          'test@example.com'
        )
        await user.type(screen.getByLabelText(/Mot de passe/), 'user@AZERTY123')
        await user.type(screen.getByLabelText(/Nom/), 'Nom')
        await user.type(screen.getByLabelText(/Prénom/), 'Prénom')

        // To simulate onBlur event
        await user.tab()

        await user.click(screen.getByRole('button', { name: 'Continuer' }))
        expect(api.signupPro).toHaveBeenCalledTimes(1)
      })

      it('should display error message when RECAPTCHA_ERROR occurs', async () => {
        const user = userEvent.setup()
        const snackBarError = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: vi.fn(),
          error: snackBarError,
        }))
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockRejectedValue(RECAPTCHA_ERROR)

        renderSignUp()
        await user.type(
          screen.getByRole('textbox', {
            name: /Adresse email */,
          }),
          'test@example.com'
        )
        await user.type(screen.getByLabelText(/Mot de passe/), 'user@AZERTY123')
        await user.type(
          screen.getByRole('textbox', {
            name: /Nom/,
          }),
          'Nom'
        )
        await user.type(
          screen.getByRole('textbox', {
            name: /Prénom/,
          }),
          'Prénom'
        )
        await user.tab()

        await user.click(screen.getByRole('button', { name: 'Continuer' }))

        await waitFor(() => {
          expect(snackBarError).toHaveBeenCalledWith(RECAPTCHA_ERROR_MESSAGE)
        })
        expect(api.signupPro).not.toHaveBeenCalled()
      })

      it('should handle non-ApiError errors', async () => {
        const user = userEvent.setup()
        const snackBarError = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: vi.fn(),
          error: snackBarError,
        }))
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        vi.spyOn(api, 'signupPro').mockRejectedValue(new Error('Network error'))

        renderSignUp()
        await user.type(
          screen.getByRole('textbox', {
            name: /Adresse email */,
          }),
          'test@example.com'
        )
        await user.type(screen.getByLabelText(/Mot de passe/), 'user@AZERTY123')
        await user.type(
          screen.getByRole('textbox', {
            name: /Nom/,
          }),
          'Nom'
        )
        await user.type(
          screen.getByRole('textbox', {
            name: /Prénom/,
          }),
          'Prénom'
        )
        await user.tab()

        await user.click(screen.getByRole('button', { name: 'Continuer' }))

        await waitFor(() => {
          expect(api.signupPro).toHaveBeenCalledTimes(1)
        })
        expect(snackBarError).toHaveBeenCalledWith(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
      })
    })
  })
})

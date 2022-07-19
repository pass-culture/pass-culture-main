import '@testing-library/jest-dom'

import * as getSirenDataAdapter from 'core/Offerers/adapters/getSirenDataAdapter'
import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router'
import { render, screen, waitFor } from '@testing-library/react'

import { Events } from 'core/FirebaseEvents/constants'
import { HTTP_STATUS } from 'api/helpers'
import { Provider } from 'react-redux'
import React from 'react'
import SignupForm from '../SignupForm'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

const mockLogEvent = jest.fn()

jest.mock('core/Offerers/adapters/getSirenDataAdapter')
jest.mock('repository/pcapi/pcapi', () => ({
  signup: jest.fn(),
}))
jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
  },
}))

const renderSignUp = storeOveride => {
  const store = configureTestStore(storeOveride)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/inscription']}>
        <Route path="/inscription">
          <SignupForm />
        </Route>
        <Route path="/accueil">
          <span>I'm logged in as a pro user</span>
        </Route>
        <Route path="/structures">
          <span>I'm logged in as an Admin</span>
        </Route>
        <Route path="/inscription/confirmation">
          <span>I'm the confirmation page</span>
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | pages | Signup | SignupForm', () => {
  let store

  beforeEach(() => {
    store = {
      user: { initialized: true },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
      app: { logEvent: mockLogEvent },
    }
    pcapi.signup.mockResolvedValue({})
  })

  it('should redirect to accueil page if the user is logged in', async () => {
    // when the user is logged in and lands on signup validation page
    store.user = {
      currentUser: {
        id: 'user_id',
        publicName: 'François',
        isAdmin: false,
      },
      initialized: true,
    }
    renderSignUp(store)
    await expect(
      screen.findByText("I'm logged in as a pro user")
    ).resolves.toBeInTheDocument()
  })

  it('should redirect to structure page if the user is logged in as an Admin', async () => {
    // when the user is logged in and lands on signup validation page
    store.user = {
      currentUser: {
        id: 'user_id',
        publicName: 'François',
        isAdmin: true,
      },
      initialized: true,
    }
    renderSignUp(store)
    await expect(
      screen.findByText("I'm logged in as an Admin")
    ).resolves.toBeInTheDocument()
  })

  describe('render', () => {
    it('should render with all information', () => {
      // when the user sees the form
      renderSignUp(store)

      // then it should have a title
      expect(
        screen.getByRole('heading', {
          name: /Créer votre compte professionnel/,
        })
      ).toBeInTheDocument()
      // and a subtitle
      expect(
        screen.getByRole('heading', {
          name: /Merci de compléter les champs suivants pour créer votre compte./,
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
        screen.getByRole('link', {
          name: /Charte des Données Personnelles/,
        })
      ).toHaveAttribute('href', 'https://pass.culture.fr/donnees-personnelles/')
      // and a mail to support
      expect(
        screen.getByRole('link', {
          name: /contactez notre support/,
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
      renderSignUp(store)
      // then it should have an email field
      expect(
        screen.getByRole('textbox', {
          name: /Adresse e-mail/,
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
      expect(
        screen.getByRole('textbox', {
          name: /Téléphone/,
        })
      ).toBeInTheDocument()
      // and a SIREN field
      expect(
        screen.getByRole('textbox', {
          name: /SIREN de la structure que vous représentez/,
        })
      ).toBeInTheDocument()
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
          const { unmount } = renderSignUp(store)
          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Adresse e-mail/,
            }),
            'test@example.com'
          )
          await userEvent.type(
            screen.getByRole('textbox', {
              name: /Téléphone/,
            }),
            '1234'
          )
          // We simulate onBlur to have email field touched
          await userEvent.tab()

          await unmount()
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
        it('should not trigger an event if no field has been touched', async () => {
          const { unmount } = renderSignUp(store)
          await unmount()
          expect(mockLogEvent).toHaveBeenCalledTimes(0)
        })
      })
      it('should have an beforeunload event listener attached to the window', async () => {
        const spyAddEvent = jest.fn()
        const spyRemoveEvent = jest.fn()
        window.addEventListener = spyAddEvent
        window.removeEventListener = spyRemoveEvent

        const { unmount } = renderSignUp(store)
        // Count calls to window.addEventListener with "beforeunload" as first argument
        expect(
          spyAddEvent.mock.calls
            .map(args => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(1)
        expect(
          spyRemoveEvent.mock.calls
            .map(args => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(0)
        await unmount()
        expect(
          spyRemoveEvent.mock.calls
            .map(args => args[0] === 'beforeunload')
            .filter(Boolean).length
        ).toEqual(1)
      })
    })
    describe('formValidation', () => {
      beforeEach(() => {
        jest.spyOn(getSirenDataAdapter, 'default').mockResolvedValue({
          isOk: true,
          message: '',
          payload: {
            values: {
              address: '4 rue du test',
              city: 'Plessix-Balisson',
              latitude: 1.1,
              longitude: 1.1,
              name: 'Ma Petite structure',
              postalCode: '22350',
              siren: '881457238',
            },
          },
        })
      })

      it('should enable submit button only when required inputs are filled and call pcapi with data', async () => {
        renderSignUp(store)
        const submitButton = screen.getByRole('button', {
          name: /Créer mon compte/,
        })
        await userEvent.type(
          screen.getByRole('textbox', {
            name: /Adresse e-mail/,
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
          screen.getByRole('textbox', {
            name: /Téléphone/,
          }),
          '0722332233'
        )
        expect(submitButton).toBeDisabled()
        await userEvent.type(
          screen.getByRole('textbox', {
            name: /SIREN/,
          }),
          '881457238'
        )

        // To simulate onBlur event
        await userEvent.tab()

        expect(submitButton).toBeEnabled()
        // Structure name should be displayed and submit button enabled
        await waitFor(() =>
          expect(
            screen.findByText('Ma Petite structure')
          ).resolves.toBeInTheDocument()
        )

        await userEvent.click(submitButton)

        expect(pcapi.signup).toHaveBeenCalledWith({
          address: '4 rue du test',
          city: 'Plessix-Balisson',
          contactOk: '',
          email: 'test@example.com',
          firstName: 'Prénom',
          lastName: 'Nom',
          latitude: 1.1,
          longitude: 1.1,
          name: 'Ma Petite structure',
          password: 'user@AZERTY123',
          phoneNumber: '0722332233',
          postalCode: '22350',
          publicName: 'Prénom',
          siren: '881457238',
        })
        await expect(
          screen.findByText("I'm the confirmation page")
        ).resolves.toBeInTheDocument()
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.SIGNUP_FORM_SUCCESS
        )
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
      })
      it('should show a notification on api call error', async () => {
        pcapi.signup.mockRejectedValue({
          errors: {
            phoneNumber: 'Le téléphone doit faire moins de 20 caractères',
          },
          status: HTTP_STATUS.GONE,
        })
        renderSignUp(store)
        const submitButton = screen.getByRole('button', {
          name: /Créer mon compte/,
        })

        await userEvent.type(
          screen.getByLabelText('Adresse e-mail'),
          'test@example.com'
        )
        await userEvent.type(
          screen.getByLabelText('Mot de passe'),
          'user@AZERTY123'
        )
        await userEvent.type(screen.getByLabelText('Nom'), 'Nom')
        await userEvent.type(screen.getByLabelText('Prénom'), 'Prénom')

        await userEvent.type(
          screen.getByLabelText(
            'Téléphone (utilisé uniquement par l’équipe du pass Culture)'
          ),
          '0722332200'
        )
        await userEvent.type(
          screen.getByLabelText('SIREN de la structure que vous représentez'),
          '881457238'
        )
        // To simulate onBlur event
        await userEvent.tab()

        await userEvent.click(submitButton)
        expect(pcapi.signup).toHaveBeenCalledTimes(1)
        expect(submitButton).toBeDisabled()

        expect(
          await screen.findByText(
            'Le téléphone doit faire moins de 20 caractères'
          )
        ).toBeInTheDocument()

        const phoneInput = screen.getByLabelText(
          'Téléphone (utilisé uniquement par l’équipe du pass Culture)'
        )
        await userEvent.clear(phoneInput)
        await userEvent.type(phoneInput, '0622332233')
        await userEvent.tab()
        await waitFor(() => expect(submitButton).toBeEnabled())
      })
      it('should display a Banner when SIREN is invisible', async () => {
        jest.spyOn(getSirenDataAdapter, 'default').mockResolvedValue({
          isOk: false,
          message: 'Ce SIREN est masqué sur le répertoire de l’INSEE.',
        })
        renderSignUp(store)
        expect(
          screen.queryByText('Modifier la visibilité de mon SIREN')
        ).not.toBeInTheDocument()
        await userEvent.type(
          screen.getByRole('textbox', {
            name: /SIREN/,
          }),
          '881457238'
        )
        // To simulate onBlur event
        await userEvent.tab()
        expect(
          screen.queryByText('Modifier la visibilité de mon SIREN')
        ).toBeInTheDocument()
      })
    })
  })
})

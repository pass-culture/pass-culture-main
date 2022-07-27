import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import {
  DIFFERENT_PASSWORDS_ERROR_MESSAGE,
  INVALID_FORM_MESSAGE,
  UNKNOWN_ERROR_MESSAGE,
} from '../SetPassword'
import SetPasswordContainer from '../SetPasswordContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  setPassword: jest.fn(),
}))

const renderSetPassword = (store, history) =>
  render(
    <Provider store={store}>
      <Router history={history}>
        <Route path="/creation-de-mot-de-passe/:token?">
          <>
            <SetPasswordContainer />
            <NotificationContainer />
          </>
        </Route>
      </Router>
    </Provider>
  )

describe('src | components | pages | SetPassword', () => {
  let store, history, historyPushSpy
  beforeEach(() => {
    store = configureTestStore()
    history = createBrowserHistory()
    history.push('/creation-de-mot-de-passe/AT3VXY5EB')
    historyPushSpy = jest.spyOn(history, 'push')
  })
  it('should redirect the user to structure page', async () => {
    // Given

    store = configureTestStore({
      user: { currentUser: { publicName: 'Bosetti' } },
    })
    renderSetPassword(store, history)

    // Then
    expect(historyPushSpy).toHaveBeenCalledWith('/accueil')
  })

  it('should render the default page without redirect', async () => {
    // Given
    renderSetPassword(store, history)

    // Then
    expect(
      screen.getByText('Bienvenue sur l’espace dédié aux acteurs culturels')
    ).toBeVisible()
  })

  it('should display form validation error on wrong confirmation', async () => {
    // Given
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    await userEvent.type(passwordInput, 'password1')
    await userEvent.type(confirmationPasswordInput, 'password2')
    await userEvent.click(submitButton)

    // Then
    expect(screen.getByText(DIFFERENT_PASSWORDS_ERROR_MESSAGE)).toBeVisible()
  })

  it('should send the right data', async () => {
    // Given
    history = createBrowserHistory()
    history.push('/creation-de-mot-de-passe/fakeToken')
    historyPushSpy = jest.spyOn(history, 'push')
    pcapi.setPassword.mockResolvedValue()
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    await userEvent.type(passwordInput, 'password1')
    await userEvent.type(confirmationPasswordInput, 'password1')
    await userEvent.click(submitButton)

    // Then
    await waitFor(() => {
      expect(pcapi.setPassword).toHaveBeenCalledWith('fakeToken', 'password1')
    })
  })

  it('should display the success message and redirect to login page', async () => {
    // Given
    pcapi.setPassword.mockResolvedValue()
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await act(async () => userEvent.click(submitButton))

    // Then
    await waitFor(() => {
      expect(history.push).toHaveBeenCalledWith(
        '/creation-de-mot-de-passe-confirmation'
      )
    })
  })

  it('should display the form error', async () => {
    // Given
    const passwordErrorMessage = 'Ton mot de passe est trop faible'
    pcapi.setPassword.mockRejectedValue({
      errors: { newPassword: [passwordErrorMessage] },
    })
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await act(async () => userEvent.click(submitButton))

    // Then
    await waitFor(() => {
      expect(screen.getByText(INVALID_FORM_MESSAGE)).toBeVisible()
      expect(
        screen.getByText(
          'Votre mot de passe doit contenir au moins : - 12 caractères - Un chiffre - Une majuscule et une minuscule - Un caractère spécial'
        )
      ).toBeVisible()
    })
  })

  it('should display the token error', async () => {
    // Given
    pcapi.setPassword.mockRejectedValue({
      errors: { token: ['token problem'] },
    })
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await act(async () => userEvent.click(submitButton))

    // Then
    await waitFor(() => {
      expect(history.push).toHaveBeenCalledWith(
        '/creation-de-mot-de-passe-confirmation?error=unvalid-link'
      )
    })
  })

  it('should display the unknown error', async () => {
    // Given
    pcapi.setPassword.mockRejectedValue({
      errors: { unknownField: ['unknown problem'] },
    })
    renderSetPassword(store, history)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await act(async () => userEvent.click(submitButton))

    // Then
    await waitFor(() => {
      expect(screen.getByText(UNKNOWN_ERROR_MESSAGE)).toBeVisible()
    })
  })

  it('should redirect the user to reset password page with a toaster when no token', async () => {
    // Given
    history = createBrowserHistory()
    history.push('/creation-de-mot-de-passe')
    historyPushSpy = jest.spyOn(history, 'push')
    renderSetPassword(store, history)

    // Then
    expect(history.push).toHaveBeenCalledWith(
      '/creation-de-mot-de-passe-confirmation?error=unvalid-link'
    )
  })
})

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import reactRouter, { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { renderWithProviders } from 'utils/renderWithProviders'

import SetPassword from '../SetPassword'

jest.mock('apiClient/api', () => ({
  api: { postNewPassword: jest.fn() },
}))
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    token: 'AT3VXY5EB',
  }),
}))

const renderSetPassword = storeOverrides =>
  renderWithProviders(
    <Routes>
      <Route
        path="/creation-de-mot-de-passe"
        element={
          <>
            <SetPassword />
            <Notification />
          </>
        }
      />
      <Route
        path="/creation-de-mot-de-passe/:token"
        element={
          <>
            <SetPassword />
            <Notification />
          </>
        }
      />
      <Route path="/accueil" element={<div>Accueil</div>} />
      <Route
        path="/creation-de-mot-de-passe-confirmation"
        element={<div>Confirmation</div>}
      />
      <Route
        path="/creation-de-mot-de-passe-erreur"
        element={<div>Error</div>}
      />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: ['/creation-de-mot-de-passe/AT3VXY5EB'],
    }
  )

describe('src | components | pages | SetPassword', () => {
  let store
  beforeEach(() => {
    store = {}
  })

  it('should redirect the user to structure page', async () => {
    // Given
    store = {
      user: { currentUser: { publicName: 'Bosetti' } },
    }
    renderSetPassword(store)

    // Then
    expect(await screen.findByText('Accueil')).toBeInTheDocument()
  })

  it('should render the default page without redirect', async () => {
    // Given
    renderSetPassword(store)

    // Then
    await waitFor(() =>
      expect(
        screen.getByText('Bienvenue sur l’espace dédié aux acteurs culturels')
      ).toBeInTheDocument()
    )
  })

  it('should display form validation error on wrong confirmation', async () => {
    // Given
    renderSetPassword(store)
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
    expect(
      screen.getByText('Les deux mots de passe ne sont pas identiques')
    ).toBeVisible()
  })

  it('should send the right data', async () => {
    // Given
    jest.spyOn(reactRouter, 'useParams').mockReturnValue({ token: 'fakeToken' })
    api.postNewPassword.mockResolvedValue()
    renderSetPassword(store)
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
    expect(api.postNewPassword).toHaveBeenCalledWith({
      token: 'fakeToken',
      newPassword: 'password1',
    })
  })

  it('should display the success message and redirect to login page', async () => {
    // Given
    api.postNewPassword.mockResolvedValue()
    renderSetPassword(store)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await userEvent.click(submitButton)

    // Then
    expect(screen.getByText('Confirmation')).toBeInTheDocument()
  })

  it('should display the form error', async () => {
    // Given
    const passwordErrorMessage = 'Ton mot de passe est trop faible'
    api.postNewPassword.mockRejectedValue(
      new ApiError(
        {},
        {
          body: { newPassword: [passwordErrorMessage] },
        },
        ''
      )
    )
    renderSetPassword(store)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await userEvent.click(submitButton)

    // Then
    expect(
      screen.getByText(
        "Une erreur s'est produite, veuillez corriger le formulaire."
      )
    ).toBeVisible()
    expect(
      screen.getByText(
        'Votre mot de passe doit contenir au moins : - 12 caractères - Un chiffre - Une majuscule et une minuscule - Un caractère spécial'
      )
    ).toBeVisible()
  })

  it('should display the token error', async () => {
    // Given
    api.postNewPassword.mockRejectedValue(
      new ApiError(
        {},
        {
          body: { token: ['token problem'] },
        },
        ''
      )
    )
    renderSetPassword(store)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await userEvent.click(submitButton)

    // Then
    expect(await screen.findByText('Error')).toBeInTheDocument()
  })

  it('should display the unknown error', async () => {
    // Given
    api.postNewPassword.mockRejectedValue(
      new ApiError(
        {},
        {
          body: { unknownField: ['unknown problem'] },
        },
        ''
      )
    )
    renderSetPassword(store)
    const passwordInput = screen.getByLabelText('Mot de passe')
    const confirmationPasswordInput = screen.getByLabelText(
      'Confirmer le mot de passe'
    )
    const submitButton = screen.getByText('Envoyer', { selector: 'button' })

    // When
    userEvent.type(passwordInput, 'password1')
    userEvent.type(confirmationPasswordInput, 'password1')
    await userEvent.click(submitButton)

    // Then
    expect(
      screen.getByText(
        "Une erreur s'est produite, veuillez contacter le support."
      )
    ).toBeVisible()
  })

  it('should redirect the user to reset password page with a toaster when no token', async () => {
    // Given
    jest.spyOn(reactRouter, 'useParams').mockReturnValue({ token: null })

    renderSetPassword(store)

    // Then
    expect(await screen.findByText('Error')).toBeInTheDocument()
  })
})

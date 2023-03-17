import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'

import SetPasswordConfirm from '../SetPasswordConfirm'

const renderSetPassword = (
  storeOverrides,
  initialRoute = '/creation-de-mot-de-passe-confirmation'
) =>
  renderWithProviders(
    <Routes>
      <Route
        path="/creation-de-mot-de-passe-confirmation"
        element={<SetPasswordConfirm />}
      />
      <Route
        path="/creation-de-mot-de-passe-erreur"
        element={<SetPasswordConfirm />}
      />
      <Route path="/accueil" element={<div>Accueil</div>} />
      <Route path="/connexion" element={<div>Connexion</div>} />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: [initialRoute],
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
    expect(
      screen.getByText('Votre mot de passe a bien été enregistré !')
    ).toBeVisible()
  })

  it('should redirect to login page on link click', async () => {
    renderSetPassword(store)

    const submitButton = screen.getByText('Se connecter', { selector: 'a' })
    userEvent.click(submitButton)

    expect(await screen.findByText('Connexion')).toBeInTheDocument()
  })

  it('should display error message when error in query params', async () => {
    renderSetPassword(store, '/creation-de-mot-de-passe-erreur')

    expect(screen.getByText('Votre lien a expiré !')).toBeVisible()
    expect(screen.getByText('Veuillez contacter notre support')).toBeVisible()
    const link = screen.getByText('Contacter')
    expect(link).toBeVisible()
    expect(link.getAttribute('href')).toBe('mailto:support-pro@passculture.app')
  })
})

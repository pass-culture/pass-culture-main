import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import Notification from 'components/Notification/Notification'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffererAuthentication } from '..'

const renderOffererAuthentiationScreen = (
  contextValue: ISignupJourneyContext
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/parcours-inscription/structure"
            element={<div>Offerer siret screen</div>}
          />
          <Route
            path="/parcours-inscription/authentification"
            element={<OffererAuthentication />}
          />
          <Route
            path="/parcours-inscription/activite"
            element={<div>Activity screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/authentification'],
    }
  )
}
describe('screens:SignupJourney::OffererAuthentication', () => {
  let contextValue: ISignupJourneyContext
  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '123 456 789 33333',
        name: 'Test name',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }
  })

  it('should render component', async () => {
    renderOffererAuthentiationScreen(contextValue)

    expect(
      await screen.findByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()

    expect(
      await screen.getByRole('heading', { level: 2, name: 'Authentification' })
    ).toBeInTheDocument()

    const siretField = screen.getByLabelText('Numéro de SIRET')
    const nameField = screen.getByLabelText('Raison sociale')

    expect(siretField).toBeDisabled()
    expect(siretField).toHaveValue('123 456 789 33333')

    expect(nameField).toBeDisabled()
    expect(nameField).toHaveValue('Test name')

    expect(
      await screen.findByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()

    expect(
      await screen.queryByRole('button', { name: 'Retour' })
    ).toBeInTheDocument()
  })

  it('should display activity screen on submit', async () => {
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.findByText('Authentification')).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(screen.getByText('Activity screen')).toBeInTheDocument()
  })

  it('should display offerer screen on submit', async () => {
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.findByText('Authentification')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer siret', async () => {
    contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.queryByText('Authentification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer name', async () => {
    contextValue.offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '12345678933333',
    }
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.queryByText('Authentification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })
})

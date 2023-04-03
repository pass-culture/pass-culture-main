import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { Target, VenueTypeCode } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import Activity from '../Activity'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../constants'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: jest.fn(),
  },
}))

const renderActivityScreen = (contextValue: ISignupJourneyContext) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
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
            path="/parcours-inscription/authentification"
            element={<div>Authentication screen</div>}
          />
          <Route path="/parcours-inscription/activite" element={<Activity />} />
          <Route
            path="/parcours-inscription/validation"
            element={<div>Validation screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: ['/parcours-inscription/activite'] }
  )
}

describe('screens:SignupJourney::Activity', () => {
  let contextValue: ISignupJourneyContext
  beforeEach(() => {
    contextValue = {
      activity: DEFAULT_ACTIVITY_FORM_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([
      { id: VenueTypeCode.MUS_E, label: 'first venue label' },
      { id: 'venue2', label: 'second venue label' },
    ])
  })

  it('should render component', async () => {
    contextValue.activity = null
    renderActivityScreen(contextValue)
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    expect(
      await screen.getByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()
    expect(await screen.getByLabelText('Activité principale')).toHaveValue('')
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter une url' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('À destination du grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText("À destination d'un groupe scolaire", {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('Les deux', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      await screen.findByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: 'Étape précédente' })
    ).toBeInTheDocument()
  })

  it('should not render component on getVenueTypes error', async () => {
    jest.spyOn(api, 'getVenueTypes').mockRejectedValue([])
    renderActivityScreen(contextValue)
    await waitFor(() => {
      expect(screen.queryByText('Activité')).not.toBeInTheDocument()
    })
  })

  it('should display validation screen on click next step button', async () => {
    contextValue.activity = {
      venueTypeCode: VenueTypeCode.MUS_E,
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL_AND_EDUCATIONAL,
    }
    renderActivityScreen(contextValue)
    expect(await screen.findByText('Activité')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should display authentification screen on click previous step button', async () => {
    renderActivityScreen(contextValue)
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape précédente' })
    )
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should display error notification', async () => {
    renderActivityScreen(contextValue)
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    await userEvent.click(screen.getByText('À destination du grand public'))
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(
      screen.getByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
    ).toBeInTheDocument()
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })
})

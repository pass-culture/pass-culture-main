import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import Activity from '../Activity'
import { IActivityFormValues } from '../ActivityForm'
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
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Activity />
    </SignupJourneyContext.Provider>,
    { storeOverrides, initialRouterEntries: ['/signup/activite'] }
  )
}

describe('screens:SignupJourney::Activity', () => {
  let contextValue: ISignupJourneyContext
  let activity: IActivityFormValues
  beforeEach(() => {
    activity = DEFAULT_ACTIVITY_FORM_VALUES

    contextValue = {
      activity: activity,
      setActivity: () => {},
      setShouldTrack: () => {},
      shouldTrack: true,
      setIsLoading: () => {},
    }
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render component', async () => {
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
      await screen.findByRole('button', { name: 'Ajouter un tarif' })
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
})

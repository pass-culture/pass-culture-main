import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import { Target } from '@/apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { Activity } from '../Activity'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
  },
}))

const renderActivityScreen = (contextValue: SignupJourneyContextValues) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/inscription/structure/activite"
            element={<Activity />}
          />
          <Route
            path="/inscription/structure/confirmation"
            element={<div>Validation screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/activite'],
    }
  )
}

describe('screens:SignupJourney::Activity', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([
      { id: 'MUSEUM', label: 'first venue label' },
      { id: 'venue2', label: 'second venue label' },
    ])
  })

  it('should render component', async () => {
    contextValue.activity = null

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Tous les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Activité principale *')).toHaveValue('')
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter un lien' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
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
    vi.spyOn(api, 'getVenueTypes').mockRejectedValue([])

    renderActivityScreen(contextValue)

    await waitFor(() => {
      expect(screen.queryByText('Activité')).not.toBeInTheDocument()
    })
  })

  it('should display validation screen on click next step button', async () => {
    contextValue.activity = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL_AND_EDUCATIONAL,
      phoneNumber: '0605120510',
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    await waitFor(() => {
      expect(screen.getByText('Validation screen')).toBeInTheDocument()
    })
  })

  it('should go next step with individual target customer', async () => {
    contextValue.activity = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL,
      phoneNumber: '0605120510',
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Au grand public')).toBeChecked()
    expect(screen.getByLabelText('À des groupes scolaires')).not.toBeChecked()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should go next step with educational target customer', async () => {
    contextValue.activity = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.EDUCATIONAL,
      phoneNumber: '0605120510',
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Au grand public')).not.toBeChecked()
    expect(screen.getByLabelText('À des groupes scolaires')).toBeChecked()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should display authentification screen on click previous step button', async () => {
    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape précédente' })
    )

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should display error notification', async () => {
    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Au grand public'))
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(
      screen.getByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })
})

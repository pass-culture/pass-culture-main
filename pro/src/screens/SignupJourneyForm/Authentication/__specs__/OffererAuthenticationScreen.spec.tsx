import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { apiAdresse } from 'apiClient/adresse'
import Notification from 'components/Notification/Notification'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffererAuthentication } from '..'

jest.mock('apiClient/adresse', () => {
  return {
    ...jest.requireActual('apiClient/adresse'),
    default: {
      getDataFromAddress: jest.fn(),
    },
  }
})

jest.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
])

// Mock https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address} called by apiAdresse.getDataFromAddress
fetch.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)

const renderOffererAuthentiationScreen = (
  contextValue: ISignupJourneyContext
) => {
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
            path="/parcours-inscription/structure"
            element={<div>Offerer siret screen</div>}
          />
          <Route
            path="/parcours-inscription/identification"
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
      initialRouterEntries: ['/parcours-inscription/identification'],
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
        address: '3 Rue de Valois',
        city: 'Paris',
        latitude: 0,
        longitude: 0,
        postalCode: '75001',
        publicName: '',
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
      await screen.getByRole('heading', { level: 2, name: 'Identification' })
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
    expect(await screen.findByText('Identification')).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(screen.getByText('Activity screen')).toBeInTheDocument()
  })

  it('should display offerer screen on submit', async () => {
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.findByText('Identification')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer siret', async () => {
    contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer name', async () => {
    contextValue.offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '12345678933333',
    }
    renderOffererAuthentiationScreen(contextValue)
    expect(await screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer siret screen')).toBeInTheDocument()
  })
})

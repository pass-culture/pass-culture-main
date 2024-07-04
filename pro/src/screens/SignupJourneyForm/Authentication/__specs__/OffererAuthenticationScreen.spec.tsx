import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse/apiAdresse'
import { Notification } from 'components/Notification/Notification'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { OffererAuthentication } from '../OffererAuthentication'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('apiClient/adresse/apiAdresse', async () => {
  return {
    ...(await vi.importActual('apiClient/adresse/apiAdresse')),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
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
fetchMock.mockResponse(
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
  contextValue: SignupJourneyContextValues
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/parcours-inscription/structure"
            element={<div>Offerer screen</div>}
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
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/identification'],
    }
  )
}
describe('screens:SignupJourney::OffererAuthentication', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '123 456 789 33333',
        name: 'Test name',
        street: '3 Rue de Valois',
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
        'Tous les champs suivis d’un * sont obligatoires.'
      )
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { level: 1, name: 'Identification' })
    ).toBeInTheDocument()

    const siretField = screen.getByLabelText('Numéro de SIRET *')
    const nameField = screen.getByLabelText('Raison sociale *')

    expect(siretField).toBeDisabled()
    expect(siretField).toHaveValue('123 456 789 33333')

    expect(nameField).toBeDisabled()
    expect(nameField).toHaveValue('Test name')

    expect(
      await screen.findByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()

    expect(screen.queryByRole('button', { name: 'Retour' })).toBeInTheDocument()
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
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer siret', () => {
    contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
    renderOffererAuthentiationScreen(contextValue)
    expect(screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer name', () => {
    contextValue.offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '12345678933333',
    }
    renderOffererAuthentiationScreen(contextValue)
    expect(screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })
})

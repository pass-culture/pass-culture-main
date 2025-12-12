import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import createFetchMock from 'vitest-fetch-mock'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'

import { OffererAuthentication } from '../OffererAuthentication'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@/apiClient/adresse/apiAdresse', async () => {
  return {
    ...(await vi.importActual('@/apiClient/adresse/apiAdresse')),
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
    inseeCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
    inseeCode: '75003',
  },
])

// Mock https://data.geopf.fr/geocodage/search/?limit=${limit}&q=${address} called by getDataFromAddress
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

const renderOffererAuthenticationScreen = (
  contextValue: SignupJourneyContextValues
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/recherche"
            element={<div>Offerer screen</div>}
          />
          <Route
            path="/inscription/structure/identification"
            element={<OffererAuthentication />}
          />
          <Route
            path="/inscription/structure/activite"
            element={<div>Activity screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/identification'],
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
        isOpenToPublic: 'true',
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress: null,
      setInitialAddress: noop,
    }
  })

  it('should render component', async () => {
    renderOffererAuthenticationScreen(contextValue)

    expect(
      await screen.findByText('Les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Retour' })).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Complétez les informations de votre structure',
      })
    ).toBeInTheDocument()

    const siretField = screen.getByLabelText(/Numéro de SIRET/)
    const nameField = screen.getByLabelText(/Raison sociale/)

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
    renderOffererAuthenticationScreen(contextValue)
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Complétez les informations de votre structure',
      })
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    await waitFor(() => {
      expect(screen.getByText('Activity screen')).toBeInTheDocument()
    })
  })

  it('should display offerer screen on submit', async () => {
    renderOffererAuthenticationScreen(contextValue)
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Complétez les informations de votre structure',
      })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  describe('not diffusible', () => {
    const context = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '923 456 789 33333',
        siren: '923 456 789',
        isDiffusible: false,
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress: null,
      setInitialAddress: noop,
    }

    it('should render the not diffusible callout', async () => {
      renderOffererAuthenticationScreen(context)

      expect(
        await screen.findByText(
          'Certaines informations de votre structure ne sont pas diffusibles.'
        )
      ).toBeInTheDocument()
    })

    it('should not render the not diffusible callout for diffusible', () => {
      renderOffererAuthenticationScreen({
        ...context,
        offerer: {
          ...context.offerer,
          isDiffusible: true,
        },
      })

      expect(
        screen.queryByText(
          'Certaines informations de votre structure ne sont pas diffusibles.'
        )
      ).not.toBeInTheDocument()
    })
  })
})

import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel, Target } from 'apiClient/v1'
import { IAddress } from 'components/Address'
import Notification from 'components/Notification/Notification'
import {
  DEFAULT_ACTIVITY_VALUES,
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Validation } from 'screens/SignupJourneyForm/Validation/index'
import { renderWithProviders } from 'utils/renderWithProviders'
jest.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: jest.fn(),
    saveNewOnboardingData: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

const addressInformations: IAddress = {
  address: '3 Rue de Valois',
  city: 'Paris',
  latitude: 1.23,
  longitude: 2.9887,
  postalCode: '75001',
}

const renderValidationScreen = (contextValue: ISignupJourneyContext) => {
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
            element={<div>Authentication</div>}
          />
          <Route
            path="/parcours-inscription/activite"
            element={<div>Activite</div>}
          />
          <Route
            path="/parcours-inscription/validation"
            element={<Validation />}
          />
          <Route path="/accueil" element={<div>accueil</div>} />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/validation'],
    }
  )
}

describe('screens:SignupJourney::Validation', () => {
  let contextValue: ISignupJourneyContext
  beforeEach(() => {
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([
      { id: 'MUSEUM', label: 'first venue label' },
      { id: 'venue2', label: 'second venue label' },
    ])
  })

  describe('Data incomplete', () => {
    it('Should redirect to authentication if no offerer is selected', async () => {
      const mockNavigate = jest.fn()
      jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)

      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/parcours-inscription/authentification'
      )
    })

    it('Should see activity screen if no activity data is set but an offerer is set', async () => {
      const mockNavigate = jest.fn()
      jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
      renderValidationScreen({
        ...contextValue,
        offerer: {
          name: 'toto',
          publicName: 'tata',
          siret: '123123123',
          ...addressInformations,
        },
      })
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(mockNavigate).toHaveBeenCalledWith(
        '/parcours-inscription/activite'
      )
    })
  })

  it('Should see the data from the previous forms for validation', async () => {
    renderValidationScreen({
      ...contextValue,
      activity: {
        venueTypeCode: 'MUSEUM',
        socialUrls: ['url1', 'url2'],
        targetCustomer: Target.EDUCATIONAL,
      },
      offerer: {
        name: 'nom',
        publicName: 'nom public',
        siret: '123123123',
        ...addressInformations,
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await screen.findByText('first venue label')).toBeInTheDocument()
    expect(screen.getByText('url1')).toBeInTheDocument()
    expect(screen.getByText('url2')).toBeInTheDocument()
    expect(screen.getByText('nom public')).toBeInTheDocument()
    expect(screen.getByText('123123123')).toBeInTheDocument()
    expect(screen.getByText('3 Rue de Valois')).toBeInTheDocument()
    expect(screen.getByText('À des groupes scolaires')).toBeInTheDocument()
  })

  describe('user actions', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueTypeCode: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          ...addressInformations,
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    it('Should navigate to activity page with the previous step button', async () => {
      const mockNavigate = jest.fn()
      jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)

      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      await userEvent.click(screen.getByText('Étape précédente'))
      expect(mockNavigate).toHaveBeenCalledWith(
        '/parcours-inscription/activite'
      )
    })

    it('Should navigate to authentication page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[0])

      expect(screen.getByText('Authentication')).toBeInTheDocument()
    })

    it('Should navigate to activite page when clicking the second update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[1])

      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('Should send the data on submit and redirect to home', async () => {
      jest
        .spyOn(api, 'saveNewOnboardingData')
        .mockResolvedValue({} as GetOffererResponseModel)
      const mockNavigate = jest.fn()
      jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer mon espace'))
      expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
        publicName: 'nom public',
        siret: '123123123',
        venueTypeCode: 'MUSEUM',
        webPresence: 'url1, url2',
        target: Target.EDUCATIONAL,
        createVenueWithoutSiret: false,
        address: '3 Rue de Valois',
        city: 'Paris',
        latitude: 1.23,
        longitude: 2.9887,
        postalCode: '75001',
      })

      expect(mockNavigate).toHaveBeenCalledWith('/accueil')
    })
  })

  describe('No public name', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueTypeCode: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          siret: '123123123',
          ...addressInformations,
          longitude: null,
          latitude: null,
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    it('Should send data with empty public name', async () => {
      jest
        .spyOn(api, 'saveNewOnboardingData')
        .mockResolvedValue({} as GetOffererResponseModel)
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer mon espace'))
      expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
        publicName: '',
        siret: '123123123',
        venueTypeCode: 'MUSEUM',
        webPresence: 'url1, url2',
        target: Target.EDUCATIONAL,
        createVenueWithoutSiret: false,
        address: '3 Rue de Valois',
        city: 'Paris',
        latitude: 0,
        longitude: 0,
        postalCode: '75001',
      })
    })

    it('Should see the data from the previous forms for validation without public name', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(await screen.findByText('first venue label')).toBeInTheDocument()
      expect(screen.getByText('nom')).toBeInTheDocument()
    })
  })

  describe('errors', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueTypeCode: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          ...addressInformations,
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    it('Should display error message on api error', async () => {
      jest.spyOn(api, 'saveNewOnboardingData').mockRejectedValue({})
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer mon espace'))
      expect(
        await screen.findByText('Erreur lors de la création de votre structure')
      ).toBeInTheDocument()
    })

    it('Should not render on venue types api error', async () => {
      jest.spyOn(api, 'getVenueTypes').mockRejectedValue({})
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(
        await screen.queryByText('Informations structure')
      ).not.toBeInTheDocument()
    })
  })
})

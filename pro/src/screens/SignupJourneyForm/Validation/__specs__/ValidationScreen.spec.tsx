import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel, Target } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_ACTIVITY_FORM_VALUES } from 'screens/SignupJourneyForm/Activity/constants'
import { Validation } from 'screens/SignupJourneyForm/Validation/index'
import { renderWithProviders } from 'utils/renderWithProviders'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: jest.fn(),
    saveNewOnboardingData: jest.fn(),
  },
}))

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
      activity: DEFAULT_ACTIVITY_FORM_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([
      { id: 'venue1', label: 'first venue label' },
      { id: 'venue2', label: 'second venue label' },
    ])
  })

  describe('Data incomplete', () => {
    it('Should see authentication screen if no offerer is selected', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(await screen.findByText('Authentication')).toBeInTheDocument()
    })

    it('Should see activity screen if no activity data is set but an offerer is set', async () => {
      renderValidationScreen({
        ...contextValue,
        offerer: {
          name: 'toto',
          publicName: 'tata',
          siret: '123123123',
          address: '3 Rue de Valois',
          city: 'Paris',
          latitude: 0,
          longitude: 0,
          postalCode: '75001',
        },
      })
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(await screen.findByText('Activite')).toBeInTheDocument()
    })
  })

  it('Should see the data from the previous forms for validation', async () => {
    renderValidationScreen({
      ...contextValue,
      activity: {
        venueType: 'venue1',
        socialUrls: ['url1', 'url2'],
        targetCustomer: Target.EDUCATIONAL,
      },
      offerer: {
        name: 'nom',
        publicName: 'nom public',
        siret: '123123123',
        address: '3 Rue de Valois',
        city: 'Paris',
        latitude: 0,
        longitude: 0,
        postalCode: '75001',
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await screen.findByText('first venue label')).toBeInTheDocument()
    expect(screen.getByText('url1')).toBeInTheDocument()
    expect(screen.getByText('url2')).toBeInTheDocument()
    expect(screen.getByText('nom public')).toBeInTheDocument()
    expect(screen.getByText('123123123')).toBeInTheDocument()
    expect(
      screen.getByText("À destination d'un groupe scolaire")
    ).toBeInTheDocument()
  })

  describe('user actions', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueType: 'venue1',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          address: '3 Rue de Valois',
          city: 'Paris',
          latitude: 0,
          longitude: 0,
          postalCode: '75001',
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    it('Should navigate to activity page with the previous step button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Étape précédente'))
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('Should navigate to authentication page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[0])
      expect(screen.getByText('Authentication')).toBeInTheDocument()
    })

    it('Should navigate to authentication page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[1])
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('Should send the data on submit', async () => {
      jest
        .spyOn(api, 'saveNewOnboardingData')
        .mockResolvedValue({} as GetOffererResponseModel)
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer mon espace'))
      expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
        name: 'nom public',
        siret: '123123123',
        venueType: 'venue1',
        webPresence: 'url1, url2',
        target: Target.EDUCATIONAL,
      })

      expect(screen.getByText('accueil')).toBeInTheDocument()
    })
  })

  describe('No public name', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueType: 'venue1',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          siret: '123123123',
          address: '3 Rue de Valois',
          city: 'Paris',
          latitude: 0,
          longitude: 0,
          postalCode: '75001',
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
        name: '',
        siret: '123123123',
        venueType: 'venue1',
        webPresence: 'url1, url2',
        target: Target.EDUCATIONAL,
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
          venueType: 'venue1',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          address: '3 Rue de Valois',
          city: 'Paris',
          latitude: 0,
          longitude: 0,
          postalCode: '75001',
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

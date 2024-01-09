import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { PostOffererResponseModel, Target } from 'apiClient/v1'
import { Address } from 'components/Address'
import Notification from 'components/Notification/Notification'
import {
  DEFAULT_ACTIVITY_VALUES,
  SignupJourneyContextValues,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Validation } from 'screens/SignupJourneyForm/Validation/index'
import * as utils from 'utils/recaptcha'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
    saveNewOnboardingData: vi.fn(),
  },
}))

const addressInformations: Address = {
  address: '3 Rue de Valois',
  city: 'Paris',
  latitude: 1.23,
  longitude: 2.9887,
  postalCode: '75001',
  banId: '75118_5995_00043',
}

const renderValidationScreen = (contextValue: SignupJourneyContextValues) => {
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
            path="/parcours-inscription/identification"
            element={<div>Authentification</div>}
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

describe('ValidationScreen', () => {
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

  it('should redirect to authentification if no offerer is selected', async () => {
    renderValidationScreen(contextValue)

    await waitFor(() => {
      expect(screen.getByText('Authentification')).toBeInTheDocument()
    })
  })

  it('should see activity screen if no activity data is set but an offerer is set', () => {
    renderValidationScreen({
      ...contextValue,
      offerer: {
        name: 'toto',
        publicName: 'tata',
        siret: '123123123',
        hasVenueWithSiret: false,
        ...addressInformations,
      },
    })
    expect(screen.getByText('Activite')).toBeInTheDocument()
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
        hasVenueWithSiret: false,
        ...addressInformations,
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await screen.findByText('first venue label')).toBeInTheDocument()
    expect(screen.getByText('url1')).toBeInTheDocument()
    expect(screen.getByText('url2')).toBeInTheDocument()
    expect(screen.getByText('nom public')).toBeInTheDocument()
    expect(screen.getByText('123123123')).toBeInTheDocument()
    expect(screen.getByText('3 Rue de Valois, 75001 Paris')).toBeInTheDocument()
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
          hasVenueWithSiret: false,
          ...addressInformations,
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

    it('Should navigate to authentification page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[0])

      expect(screen.getByText('Authentification')).toBeInTheDocument()
    })

    it('Should navigate to activite page when clicking the second update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[1])

      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('Should redirect to home after submit', async () => {
      vi.spyOn(api, 'saveNewOnboardingData').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(await screen.findByText('accueil')).toBeInTheDocument()
    })
  })

  describe('Data sending tests', () => {
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
          hasVenueWithSiret: false,
          ...addressInformations,
          longitude: null,
          latitude: null,
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    const publicNames = ['nom public', '']
    it.each(publicNames)(
      'Should send data with name %s',
      async (publicName: string) => {
        if (contextValue.offerer) {
          contextValue.offerer.publicName = publicName
        }
        vi.spyOn(api, 'saveNewOnboardingData').mockResolvedValue(
          {} as PostOffererResponseModel
        )
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        renderValidationScreen(contextValue)
        await waitForElementToBeRemoved(() =>
          screen.queryAllByTestId('spinner')
        )
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
          publicName: publicName,
          siret: '123123123',
          venueTypeCode: 'MUSEUM',
          webPresence: 'url1, url2',
          target: Target.EDUCATIONAL,
          createVenueWithoutSiret: false,
          address: '3 Rue de Valois',
          banId: '75118_5995_00043',
          city: 'Paris',
          latitude: 0,
          longitude: 0,
          postalCode: '75001',
          token: 'token',
        })
      }
    )

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
          hasVenueWithSiret: false,
          ...addressInformations,
        },
        setActivity: () => {},
        setOfferer: () => {},
      }
    })

    it('Should display error message on api error', async () => {
      vi.spyOn(api, 'saveNewOnboardingData').mockRejectedValue({})
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(
        await screen.findByText('Erreur lors de la création de votre structure')
      ).toBeInTheDocument()
    })

    it('Should not render on venue types api error', async () => {
      vi.spyOn(api, 'getVenueTypes').mockRejectedValue({})
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(
        screen.queryByText('Informations structure')
      ).not.toBeInTheDocument()
    })
  })
})

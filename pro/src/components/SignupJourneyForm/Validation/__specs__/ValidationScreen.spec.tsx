import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  PostOffererResponseModel,
  Target,
} from 'apiClient/v1'
import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { DEFAULT_ACTIVITY_VALUES } from 'commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Address } from 'commons/core/shared/types'
import { getOffererNameFactory } from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import * as utils from 'commons/utils/recaptcha'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'
import { Validation } from 'components/SignupJourneyForm/Validation/Validation'
import { Route, Routes } from 'react-router'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
    saveNewOnboardingData: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

const useHasAccessToDidacticOnboarding = vi.hoisted(() => vi.fn())
vi.mock('commons/hooks/useHasAccessToDidacticOnboarding', () => ({
  useHasAccessToDidacticOnboarding,
}))

const selectCurrentOffererId = vi.hoisted(() => vi.fn())
vi.mock('commons/store/offerer/selectors', async (importOriginal) => ({
  ...(await importOriginal()),
  selectCurrentOffererId,
}))

const addressInformations: Address = {
  street: '3 Rue de Valois',
  city: 'Paris',
  latitude: 1.23,
  longitude: 2.9887,
  postalCode: '75001',
  inseeCode: '75111',
  banId: '75118_5995_00043',
}

const renderValidationScreen = (contextValue: SignupJourneyContextValues) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentification</div>}
          />
          <Route
            path="/inscription/structure/activite"
            element={<div>Activite</div>}
          />
          <Route
            path="/inscription/structure/confirmation"
            element={<Validation />}
          />
          <Route path="/accueil" element={<div>accueil</div>} />
          <Route path="/onboarding" element={<div>onboarding</div>} />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/confirmation'],
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

  it('should see activity screen if no activity data is set but an offerer is set', async () => {
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
    await waitFor(() => {
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })
  })

  it('should see the data from the previous forms for validation', async () => {
    renderValidationScreen({
      ...contextValue,
      activity: {
        venueTypeCode: 'MUSEUM',
        socialUrls: ['url1', 'url2'],
        targetCustomer: Target.EDUCATIONAL,
        phoneNumber: '',
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
          phoneNumber: '',
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
      selectCurrentOffererId.mockReturnValue(null)
    })

    it('should navigate to activity page with the previous step button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      await userEvent.click(screen.getByText('Étape précédente'))
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('should navigate to authentification page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[0])

      expect(screen.getByText('Authentification')).toBeInTheDocument()
    })

    it('should navigate to activite page when clicking the second update button', async () => {
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      await userEvent.click(screen.getAllByText('Modifier')[1])

      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    describe('form validation', () => {
      beforeEach(() => {
        vi.spyOn(api, 'saveNewOnboardingData').mockResolvedValue({
          id: 1,
        } as PostOffererResponseModel)
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
          offerersNames: [getOffererNameFactory({ id: 10 })],
        })
      })

      it("should redirect to home after submit if user doesn't have access to onBoarding", async () => {
        useHasAccessToDidacticOnboarding.mockReturnValue(false)
        renderValidationScreen(contextValue)
        await waitForElementToBeRemoved(() =>
          screen.queryAllByTestId('spinner')
        )
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        expect(await screen.findByText('accueil')).toBeInTheDocument()
      })

      it('should redirect to onboarding after submit if user has access to onBoarding and the offerer is not activated', async () => {
        useHasAccessToDidacticOnboarding.mockReturnValue(true)
        selectCurrentOffererId.mockReturnValue(null)
        renderValidationScreen(contextValue)
        await waitForElementToBeRemoved(() =>
          screen.queryAllByTestId('spinner')
        )
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        expect(await screen.findByText('onboarding')).toBeInTheDocument()
      })

      it('should redirect to home after submit if user has access to onBoarding, but he added a structure that is already onBoarded', async () => {
        useHasAccessToDidacticOnboarding.mockReturnValue(true)
        selectCurrentOffererId.mockReturnValue(10)
        vi.spyOn(api, 'getOfferer').mockResolvedValue({
          isOnboarded: true,
        } as GetOffererResponseModel)

        renderValidationScreen(contextValue)
        await waitForElementToBeRemoved(() =>
          screen.queryAllByTestId('spinner')
        )
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        expect(await screen.findByText('accueil')).toBeInTheDocument()
      })

      it('should redirect to onboarding after submit if user has access to onBoarding, and he added a structure that not onBoarded yet', async () => {
        useHasAccessToDidacticOnboarding.mockReturnValue(true)
        selectCurrentOffererId.mockReturnValue(10)
        vi.spyOn(api, 'getOfferer').mockResolvedValue({
          isOnboarded: false,
        } as GetOffererResponseModel)

        renderValidationScreen(contextValue)
        await waitForElementToBeRemoved(() =>
          screen.queryAllByTestId('spinner')
        )
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        expect(await screen.findByText('onboarding')).toBeInTheDocument()
      })
    })
  })

  describe('Data sending tests', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          venueTypeCode: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
          phoneNumber: '',
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
      'should send data with name %s',
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
          address: {
            street: '3 Rue de Valois',
            banId: '75118_5995_00043',
            city: 'Paris',
            latitude: 0,
            longitude: 0,
            postalCode: '75001',
            inseeCode: '75111',
          },
          token: 'token',
          isOpenToPublic: false,
          phoneNumber: '',
        })
      }
    )

    it('should see the data from the previous forms for validation without public name', async () => {
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
          phoneNumber: '',
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

    it('should display error message on api error', async () => {
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

    it('should not render on venue types api error', async () => {
      vi.spyOn(api, 'getVenueTypes').mockRejectedValue({})
      renderValidationScreen(contextValue)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      expect(
        screen.queryByText('Informations structure')
      ).not.toBeInTheDocument()
    })
  })
})

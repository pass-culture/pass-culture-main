import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import { type PostOffererResponseModel, Target } from '@/apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { RECAPTCHA_ERROR } from '@/commons/core/shared/constants'
import type { Address } from '@/commons/core/shared/types'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import * as utils from '@/commons/utils/recaptcha'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Validation } from '@/components/SignupJourneyForm/Validation/Validation'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
    saveNewOnboardingData: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

const selectCurrentOffererId = vi.hoisted(() => vi.fn())
vi.mock('@/commons/store/offerer/selectors', async (importOriginal) => ({
  ...(await importOriginal()),
  selectCurrentOffererId,
}))

const setSelectedOffererByIdMock = vi.hoisted(() => vi.fn())
vi.mock('@/commons/store/user/dispatchers/setSelectedOffererById', () => ({
  setSelectedOffererById: (args: unknown) => {
    return () => setSelectedOffererByIdMock(args)
  },
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

const renderValidationScreen = (
  contextValue: SignupJourneyContextValues,
  options?: RenderWithProvidersOptions
) => {
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
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/confirmation'],
      ...options,
    }
  )
}

const createMockPromise = (value: string) => {
  const p: any = Promise.resolve({
    type: 'user/setSelectedOffererById/fulfilled',
    payload: value,
  })
  p.unwrap = () => Promise.resolve(value)
  return p
}

describe('ValidationScreen', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress: null,
      setInitialAddress: noop,
    }
    setSelectedOffererByIdMock.mockReset()
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
        isDiffusible: true,
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
        activity: 'MUSEUM',
        socialUrls: ['url1', 'url2'],
        targetCustomer: Target.EDUCATIONAL,
        phoneNumber: '',
        culturalDomains: undefined,
      },
      offerer: {
        name: 'nom',
        publicName: 'nom public',
        siret: '123123123',
        hasVenueWithSiret: false,
        isDiffusible: true,
        ...addressInformations,
      },
    })
    expect(await screen.findByText('Musée')).toBeInTheDocument()
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
          activity: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
          phoneNumber: '',
          culturalDomains: undefined,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          hasVenueWithSiret: false,
          isDiffusible: true,
          ...addressInformations,
        },
        setActivity: () => {},
        setOfferer: () => {},
        initialAddress: null,
        setInitialAddress: noop,
      }
      selectCurrentOffererId.mockReturnValue(null)
    })

    it('should navigate to activity page with the previous step button', async () => {
      renderValidationScreen(contextValue)

      await userEvent.click(screen.getByText('Étape précédente'))
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('should navigate to authentification page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getAllByText('Modifier')[0])

      expect(screen.getByText('Authentification')).toBeInTheDocument()
    })

    it('should navigate to activite page when clicking the second update button', async () => {
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getAllByText('Modifier')[1])

      expect(screen.getByText('Activite')).toBeInTheDocument()
    })
  })

  describe('Data sending tests', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
          phoneNumber: '',
          culturalDomains: undefined,
        },
        offerer: {
          name: 'nom',
          siret: '123123123',
          hasVenueWithSiret: false,
          isDiffusible: true,
          ...addressInformations,
          longitude: null,
          latitude: null,
        },
        setActivity: () => {},
        setOfferer: () => {},
        initialAddress: null,
        setInitialAddress: noop,
      }
      // Mock par défaut pour setSelectedOffererById
      setSelectedOffererByIdMock.mockReturnValue(createMockPromise('full'))
    })

    it('should send data with public name', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = 'nom public'
      }
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      vi.spyOn(api, 'saveNewOnboardingData').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
        activity: 'MUSEUM',
        culturalDomains: undefined,
        publicName: 'nom public',
        siret: '123123123',
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
          isManualEdition: false,
        },
        token: 'token',
        isOpenToPublic: false,
        phoneNumber: '',
      })
    })

    it('should send data without public name', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = ''
      }
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      vi.spyOn(api, 'saveNewOnboardingData').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(api.saveNewOnboardingData).toHaveBeenCalledWith({
        culturalDomains: undefined,
        activity: 'MUSEUM',
        publicName: null,
        siret: '123123123',
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
          isManualEdition: false,
        },
        token: 'token',
        isOpenToPublic: false,
        phoneNumber: '',
      })
    })

    it('should send activity when offerer is open to public', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = 'nom public'
        contextValue.offerer.isOpenToPublic = 'true'
      }
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      const saveNewOnboardingDataMock = vi
        .spyOn(api, 'saveNewOnboardingData')
        .mockResolvedValue({} as PostOffererResponseModel)
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      renderValidationScreen(contextValue)
      expect(screen.getByText('Musée')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(saveNewOnboardingDataMock).toHaveBeenCalledTimes(1)
      const [[payload]] = saveNewOnboardingDataMock.mock.calls
      expect(payload.activity).toBe('MUSEUM')
    })

    it('should see the data from the previous forms for validation without public name', async () => {
      renderValidationScreen(contextValue)
      expect(await screen.findByText('Musée')).toBeInTheDocument()
      expect(screen.getByText('nom')).toBeInTheDocument()
    })

    it('should send cultural domains', async () => {
      if (contextValue.activity) {
        contextValue.activity.culturalDomains = [
          'Domaine 1',
          'Domaine II',
          'Domaine C',
        ]
      }
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      const saveNewOnboardingDataMock = vi
        .spyOn(api, 'saveNewOnboardingData')
        .mockResolvedValue({} as PostOffererResponseModel)
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      renderValidationScreen(contextValue)
      expect(
        screen.getByText('Domaine 1, Domaine II, Domaine C')
      ).toBeInTheDocument()
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(saveNewOnboardingDataMock).toHaveBeenCalledTimes(1)
      const [[payload]] = saveNewOnboardingDataMock.mock.calls
      expect(payload.culturalDomains).toEqual([
        'Domaine 1',
        'Domaine II',
        'Domaine C',
      ])
    })
  })

  describe('errors', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: 'MUSEUM',
          socialUrls: ['url1', 'url2'],
          targetCustomer: Target.EDUCATIONAL,
          phoneNumber: '',
          culturalDomains: undefined,
        },
        offerer: {
          name: 'nom',
          publicName: 'nom public',
          siret: '123123123',
          hasVenueWithSiret: false,
          isDiffusible: true,
          ...addressInformations,
        },
        setActivity: () => {},
        setOfferer: () => {},
        initialAddress: null,
        setInitialAddress: noop,
      }
    })

    it('should display error message on api error', async () => {
      vi.spyOn(api, 'saveNewOnboardingData').mockRejectedValue({})
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(
        await screen.findByText('Erreur lors de la création de votre structure')
      ).toBeInTheDocument()
    })

    it('should not render when no activity', () => {
      const noActivityContext = { ...contextValue, activity: null }
      renderValidationScreen(noActivityContext)
      expect(
        screen.queryByText('Informations structure')
      ).not.toBeInTheDocument()
    })

    it('should not render when no offerer', () => {
      const noOffererContext = { ...contextValue, offerer: null }
      renderValidationScreen(noOffererContext)
      expect(
        screen.queryByText('Informations structure')
      ).not.toBeInTheDocument()
    })

    it('should display recaptcha error message when recaptcha error occurs', async () => {
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockRejectedValue(RECAPTCHA_ERROR)
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(
        await screen.findByText('Une erreur technique est survenue')
      ).toBeInTheDocument()
    })
  })
})

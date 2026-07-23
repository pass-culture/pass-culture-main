import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import {
  ActivityOpenToPublic,
  type PostOffererResponseModel,
  Target,
} from '@/apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import type { Address } from '@/commons/context/SignupJourneyContext/types'
import { RECAPTCHA_ERROR } from '@/commons/core/shared/constants'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from '@/commons/utils/localStorageManager'
import { noop } from '@/commons/utils/noop'
import * as utils from '@/commons/utils/recaptcha'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Validation } from '@/components/SignupJourneyForm/Validation/Validation'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

const inMemoryLocalStorage = new Map<string, string>()

const initialAddress = {
  addressAutocomplete: '3 Rue de Valois 75001 Paris',
  'search-addressAutocomplete': '3 Rue de Valois 75001 Paris',
  street: '3 Rue de Valois',
  city: 'Paris',
  postalCode: '75001',
  inseeCode: '75111',
  latitude: 1.23,
  longitude: 2.34,
  coords: '',
  manuallySetAddress: false,
  banId: '',
} as const

vi.mock('@/commons/utils/localStorageManager', async () => {
  const actual = await vi.importActual('@/commons/utils/localStorageManager')

  return {
    ...actual,
    localStorageManager: {
      getItem: vi.fn((key: LocalStorageKeyType) => {
        return inMemoryLocalStorage.get(key) ?? null
      }),
      setItem: vi.fn((key: LocalStorageKeyType, value: string) => {
        inMemoryLocalStorage.set(key, value)
      }),
      removeItem: vi.fn((key: LocalStorageKeyType) => {
        inMemoryLocalStorage.delete(key)
      }),
      clear: vi.fn(() => {
        inMemoryLocalStorage.clear()
      }),
    },
  }
})

vi.mock('@/apiClient/api', () => ({
  api: {
    structureSignup: vi.fn(),
  },
}))

const initializeUserMock = vi.hoisted(() => vi.fn())
vi.mock('@/commons/store/user/dispatchers/initializeUser', () => ({
  initializeUser: (args: unknown) => {
    return () => initializeUserMock(args)
  },
}))

vi.mock('@/app/AppRouter/utils/getUserDefaultPath', () => ({
  getUserDefaultPath: vi.fn(() => '/accueil'),
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
            path="/inscription/structure/recherche"
            element={<div>Offerer search</div>}
          />
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
          <Route
            path="/rattachement-en-cours"
            element={<div>rattachement</div>}
          />
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

const createMockInitializeUserPromise = () => {
  const p: any = Promise.resolve({
    type: 'user/initializeUser/fulfilled',
  })
  p.unwrap = () => Promise.resolve()
  return p
}

describe('ValidationScreen', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    inMemoryLocalStorage.clear()
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress,
      setInitialAddress: noop,
    }
    initializeUserMock.mockReset()
  })

  it('should redirect to authentification if no offerer is selected', async () => {
    renderValidationScreen(contextValue)

    await waitFor(() => {
      expect(screen.getByText('Offerer search')).toBeInTheDocument()
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
      expect(screen.getByText('Offerer search')).toBeInTheDocument()
    })
  })

  it('should see the data from the previous forms for validation', async () => {
    renderValidationScreen({
      ...contextValue,
      activity: {
        activity: ActivityOpenToPublic.MUSEUM,
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
    expect(screen.getByText('nom')).toBeInTheDocument()
    expect(screen.getByText('nom public')).toBeInTheDocument()
    expect(screen.getByText('123 123 123')).toBeInTheDocument()
    expect(screen.getByText('3 Rue de Valois, 75001 Paris')).toBeInTheDocument()
    expect(
      screen.getByText('Aux groupes scolaires via ADAGE')
    ).toBeInTheDocument()
  })

  it('should display "non diffusée" if the offerer is not diffusible', async () => {
    renderValidationScreen({
      ...contextValue,
      activity: {
        activity: ActivityOpenToPublic.MUSEUM,
        socialUrls: ['url1', 'url2'],
        targetCustomer: Target.EDUCATIONAL,
        phoneNumber: '',
        culturalDomains: ['Domaine 1', 'Domaine 2', 'Domaine 3'],
      },
      offerer: {
        name: '',
        publicName: 'nom public',
        siret: '123123123',
        hasVenueWithSiret: false,
        isDiffusible: false,
        ...addressInformations,
        street: 'Adresse non diffusée',
      },
    })
    expect(await screen.findByText('Musée')).toBeInTheDocument()
    expect(screen.getByText('url1')).toBeInTheDocument()
    expect(screen.getByText('url2')).toBeInTheDocument()
    expect(screen.getByText('Domaines d’activité')).toBeInTheDocument()
    expect(screen.getByText('Domaine 1')).toBeInTheDocument()
    expect(screen.getByText('Domaine 2')).toBeInTheDocument()
    expect(screen.getByText('Domaine 3')).toBeInTheDocument()
    expect(screen.getByText('Non diffusée')).toBeInTheDocument()
    expect(screen.getByText('nom public')).toBeInTheDocument()
    expect(screen.getByText('123 123 123')).toBeInTheDocument()
    expect(
      screen.getByText('Adresse non diffusée, 75001 Paris')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Aux groupes scolaires via ADAGE')
    ).toBeInTheDocument()
  })

  describe('when WIP_PRE_SIGNUP_SIMULATION is enabled', () => {
    it('should display new heading and subtitle', () => {
      renderValidationScreen(
        {
          ...contextValue,
          activity: {
            activity: ActivityOpenToPublic.MUSEUM,
            socialUrls: ['url1'],
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
        },
        { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
      )

      expect(
        screen.getByRole('heading', {
          level: 1,
          name: 'Vérifiez vos informations',
        })
      ).toBeInTheDocument()

      expect(
        screen.getByRole('heading', { level: 2, name: 'Votre structure' })
      ).toBeInTheDocument()

      expect(
        screen.queryByRole('heading', { level: 2, name: 'Vos informations' })
      ).not.toBeInTheDocument()
    })
  })

  describe('user actions', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: ActivityOpenToPublic.MUSEUM,
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
        initialAddress,
        setInitialAddress: noop,
      }
    })

    it('should navigate to activity page with the previous step button', async () => {
      renderValidationScreen(contextValue)

      await userEvent.click(screen.getByText('Retour'))
      expect(screen.getByText('Activite')).toBeInTheDocument()
    })

    it('should navigate to authentification page when clicking the first update button', async () => {
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getAllByText('Modifier')[0])

      expect(screen.getByText('Authentification')).toBeInTheDocument()
    })

    it('should navigate to activity page when clicking the second update button', async () => {
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getAllByText('Modifier')[1])

      expect(screen.getByText('Activite')).toBeInTheDocument()
    })
  })

  describe('Data sending tests', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: ActivityOpenToPublic.MUSEUM,
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
        initialAddress,
        setInitialAddress: noop,
      }
      initializeUserMock.mockReturnValue(createMockInitializeUserPromise())
    })

    it('should send data with public name', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = 'nom public'
      }
      vi.spyOn(api, 'structureSignup').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(api.structureSignup).toHaveBeenCalledWith({
        body: {
          activity: 'MUSEUM',
          otherActivityComment: null,
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
        },
      })
    })

    it('should send data without public name', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = ''
      }
      vi.spyOn(api, 'structureSignup').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(api.structureSignup).toHaveBeenCalledWith({
        body: {
          culturalDomains: undefined,
          activity: 'MUSEUM',
          otherActivityComment: null,
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
        },
      })
    })

    it('should send activity when offerer is open to public', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.publicName = 'nom public'
        contextValue.offerer.isOpenToPublic = 'true'
      }
      const saveNewOnboardingDataMock = vi
        .spyOn(api, 'structureSignup')
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
      expect(payload.body.activity).toBe('MUSEUM')
    })

    it('should send cultural domains', async () => {
      if (contextValue.activity) {
        contextValue.activity.culturalDomains = [
          'Domaine 1',
          'Domaine II',
          'Domaine C',
        ]
      }
      const saveNewOnboardingDataMock = vi
        .spyOn(api, 'structureSignup')
        .mockResolvedValue({} as PostOffererResponseModel)
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      renderValidationScreen(contextValue)
      expect(screen.getByText('Domaines d’activité')).toBeInTheDocument()
      expect(screen.getByText('Domaine 1')).toBeInTheDocument()
      expect(screen.getByText('Domaine II')).toBeInTheDocument()
      expect(screen.getByText('Domaine C')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(saveNewOnboardingDataMock).toHaveBeenCalledTimes(1)
      const [[payload]] = saveNewOnboardingDataMock.mock.calls
      expect(payload.body.culturalDomains).toEqual([
        'Domaine 1',
        'Domaine II',
        'Domaine C',
      ])
    })

    it('should send other activity comment if activity is OTHER', async () => {
      if (contextValue.activity) {
        contextValue.activity.activity = ActivityOpenToPublic.OTHER
        contextValue.activity.otherActivityComment = 'urbex en pleine nature'
      }
      vi.spyOn(api, 'structureSignup').mockResolvedValue(
        {} as PostOffererResponseModel
      )
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      renderValidationScreen(contextValue)
      await userEvent.click(screen.getByText('Valider et créer ma structure'))
      expect(api.structureSignup).toHaveBeenCalledWith({
        body: {
          culturalDomains: undefined,
          activity: 'OTHER',
          otherActivityComment: 'urbex en pleine nature',
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
        },
      })
    })

    describe('navigation after creation', () => {
      beforeEach(() => {
        vi.spyOn(api, 'structureSignup').mockResolvedValue(
          {} as PostOffererResponseModel
        )
        vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
          remove: vi.fn(),
        } as unknown as HTMLScriptElement)
        vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
        initializeUserMock.mockReturnValue(createMockInitializeUserPromise())
      })

      it('should navigate to user default path after creation', async () => {
        renderValidationScreen(contextValue)
        await userEvent.click(screen.getByText('Valider et créer ma structure'))
        await waitFor(() => {
          expect(initializeUserMock).toHaveBeenCalled()
        })
        expect(screen.getByText('accueil')).toBeInTheDocument()
      })
    })
  })

  describe('venue handling', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: ActivityOpenToPublic.MUSEUM,
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
        initialAddress,
        setInitialAddress: noop,
      }
    })

    it('should call initializeUser with newOffererId and navigate to user default path', async () => {
      const createdOfferer = { id: 42 } as PostOffererResponseModel
      vi.spyOn(api, 'structureSignup').mockResolvedValue(createdOfferer)
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      const initPromise = Promise.resolve({
        type: 'user/initializeUser/fulfilled',
      }) as any
      initPromise.unwrap = () => Promise.resolve()
      initializeUserMock.mockReturnValue(initPromise)

      renderValidationScreen(contextValue)

      await userEvent.click(screen.getByText('Valider et créer ma structure'))

      await waitFor(() => {
        expect(initializeUserMock).toHaveBeenCalledWith(
          expect.objectContaining({ newOffererId: 42 })
        )
      })
      expect(screen.getByText('accueil')).toBeInTheDocument()
    })
  })

  describe('errors', () => {
    beforeEach(() => {
      contextValue = {
        activity: {
          activity: ActivityOpenToPublic.MUSEUM,
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
        initialAddress,
        setInitialAddress: noop,
      }
    })

    it('should display error message on api error', async () => {
      vi.spyOn(api, 'structureSignup').mockRejectedValue({})
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

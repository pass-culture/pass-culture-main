import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import {
  SignupJourneyContext,
  SignupJourneyContextProvider,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import * as getSiretData from '@/commons/core/Venue/utils/getSiretData'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { structureDataBodyModelFactory } from '@/commons/utils/factories/userOfferersFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { ApiError } from 'apiClient/compat'
import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import { Offerer } from './Offerer'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const inMemoryLocalStorage = new Map<string, string>()

vi.mock('@/commons/context/SignupJourneyContext/storage', async () => {
  const actual = await vi.importActual(
    '@/commons/context/SignupJourneyContext/storage'
  )

  return {
    ...actual,
    cleanSignupJourneyStorage: vi.fn(() => {
      inMemoryLocalStorage.clear()
    }),
    tryRestoreActivityFromStorage: vi.fn(() => {
      return (
        inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY) ||
        null
      )
    }),
    tryRestoreOffererFromStorage: vi.fn(() => {
      const offererStr = inMemoryLocalStorage.get(
        LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER
      )
      return offererStr ? JSON.parse(offererStr) : null
    }),
    tryRestoreInitialAddressFromStorage: vi.fn(() => {
      const addressStr = inMemoryLocalStorage.get(
        LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
      )
      return addressStr ? JSON.parse(addressStr) : null
    }),
  }
})

vi.mock('@/commons/utils/localStorageManager', async () => {
  const actual = await vi.importActual('@/commons/utils/localStorageManager')

  return {
    ...actual,
    localStorageManager: {
      getItem: vi.fn((key: LOCAL_STORAGE_KEY) => {
        return inMemoryLocalStorage.get(key) ?? null
      }),
      setItem: vi.fn((key: LOCAL_STORAGE_KEY, value: string) => {
        inMemoryLocalStorage.set(key, value)
      }),
      removeItem: vi.fn((key: LOCAL_STORAGE_KEY) => {
        inMemoryLocalStorage.delete(key)
      }),
      clear: vi.fn(() => {
        inMemoryLocalStorage.clear()
      }),
    },
  }
})

// Mock l’appel à https://data.geopf.fr/geocodage/search/?limit=${limit}&q=${address}
// Appel fait dans getDataFromAddress
vi.mock('@/apiClient/adresse/apiAdresse', () => ({
  getDataFromAddressParts: () =>
    Promise.resolve([
      {
        address: 'name',
        city: 'city',
        id: 'id',
        latitude: 0,
        longitude: 0,
        label: 'label',
        postalCode: 'postcode',
      },
    ]),
}))

// Disable memoization because getSiretData value needs to change
vi.mock('@/commons/utils/memoize', () => ({
  memoize: (func: unknown) => func,
}))

const renderOffererScreen = (
  contextValue: SignupJourneyContextValues,
  features: string[] = []
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/recherche"
            element={<Offerer />}
          />
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/inscription/structure/rattachement"
            element={<div>Offerers screen</div>}
          />
          <Route path="/hub" element={<div>Hub screen</div>} />
        </Routes>
      </SignupJourneyContext.Provider>
      <SnackBarContainer />
    </>,
    {
      features,
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche'],
    }
  )
}

const renderRealOffererScreen = (features: string[] = []) => {
  return renderWithProviders(
    <>
      <SignupJourneyContextProvider>
        <Routes>
          <Route
            path="/inscription/structure/recherche"
            element={<Offerer />}
          />
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/inscription/structure/rattachement"
            element={<div>Offerers screen</div>}
          />
          <Route path="/hub" element={<div>Hub screen</div>} />
        </Routes>
      </SignupJourneyContextProvider>
      <SnackBarContainer />
    </>,
    {
      features,
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche'],
    }
  )
}

const mockSetOfferer = vi.fn()
const mockSetInitialAddress = vi.fn()
const mockSetActivity = vi.fn()

describe('Offerer', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    inMemoryLocalStorage.clear()

    contextValue = {
      activity: null,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: mockSetActivity,
      setOfferer: mockSetOfferer,
      initialAddress: null,
      setInitialAddress: mockSetInitialAddress,
    }

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })

    vi.spyOn(api, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
  })

  describe('Restore contexts from storage', () => {
    it('should try to restore offerer and initialAddress and reset the form when context is missing', async () => {
      renderRealOffererScreen()

      await waitFor(() => {
        expect(tryRestoreOffererFromStorage).toHaveBeenCalled()
        expect(tryRestoreInitialAddressFromStorage).toHaveBeenCalled()
      })
    })

    it('should try to restore offerer and initialAddress when context equals default values', async () => {
      renderRealOffererScreen()

      await waitFor(() => {
        expect(tryRestoreOffererFromStorage).toHaveBeenCalled()
        expect(tryRestoreInitialAddressFromStorage).toHaveBeenCalled()
      })
    })
  })

  it('should render component', async () => {
    contextValue.offerer = null
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Renseignez le SIRET de la structure à laquelle vous êtes rattaché.'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Étape précédente' })
    ).not.toBeInTheDocument()
  })

  describe('when WIP_PRE_SIGNUP_SIMULATION is enabled', () => {
    it('should display new heading and hide old subtitle and ActionBar', async () => {
      contextValue.offerer = null
      renderOffererScreen(contextValue, ['WIP_PRE_SIGNUP_SIMULATION'])

      expect(
        await screen.findByRole('heading', { name: 'Votre numéro SIRET' })
      ).toBeInTheDocument()

      expect(
        screen.getByText(/Le SIRET est un identifiant à 14 chiffres/)
      ).toBeInTheDocument()

      expect(
        screen.queryByText('Dites-nous pour quelle structure vous travaillez')
      ).not.toBeInTheDocument()

      expect(
        screen.queryByRole('button', { name: 'Annuler et quitter' })
      ).not.toBeInTheDocument()

      expect(
        screen.getByRole('button', { name: 'Continuer' })
      ).toBeInTheDocument()
    })
  })

  it('should not display authentication screen on submit with form error', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: ["Le SIRET n'existe pas"],
          },
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    expect(
      screen.getByText('Dites-nous pour quelle structure vous travaillez')
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(screen.queryByText('Authentication screen')).not.toBeInTheDocument()
    expect(
      screen.getByText('Dites-nous pour quelle structure vous travaillez')
    ).toBeInTheDocument()
  })

  it('should not render offerers screen on submit if venuesList is empty', async () => {
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Dites-nous pour quelle structure vous travaillez'
      )
    ).toBeInTheDocument()
    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(screen.queryByText('Offerers screen')).not.toBeInTheDocument()
  })

  it('should submit the form when clicking the continue button', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        {
          id: 1,
          name: 'Venue Name 1',
          publicName: 'Venue Public Name 1',
          isPermanent: true,
        },
        {
          id: 2,
          name: 'Venue Name 2',
          publicName: 'Venue Public Name 2',
          isPermanent: true,
        },
      ],
    })
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetInitialAddress).toHaveBeenCalledWith({
      banId: '49759_1304_00002',
      city: 'Paris',
      inseeCode: '75056',
      latitude: 48.869440910282734,
      longitude: 2.3087717501609233,
      postalCode: '75001',
      street: '4 rue Carnot',
      addressAutocomplete: '4 rue Carnot 75001 Paris',
      'search-addressAutocomplete': '4 rue Carnot 75001 Paris',
    })
    expect(mockSetOfferer).toHaveBeenCalledWith({
      apeCode: '9003A',
      hasVenueWithSiret: false,
      name: 'ma super stucture',
      siren: '123456789',
      siret: '12345678933333',
      banId: '49759_1304_00002',
      city: 'Paris',
      inseeCode: '75056',
      latitude: 48.869440910282734,
      longitude: 2.3087717501609233,
      postalCode: '75001',
      street: '4 rue Carnot',
      isDiffusible: true,
      isOpenToPublic: undefined,
    })
    expect(api.getVenuesOfOffererFromSiret).toHaveBeenCalled()
  })

  it('should redirect to offerers page if the offerer has a venue with the same siret', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        {
          id: 1,
          name: 'Venue Name 1',
          publicName: 'Venue Public Name 1',
          isPermanent: true,
          siret: '12345678933333',
        },
        {
          id: 2,
          name: 'Venue Name 2',
          publicName: 'Venue Public Name 2',
          isPermanent: true,
        },
      ],
    })
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue({
      location: null,
      apeCode: '75',
      isDiffusible: true,
      name: 'name',
      siren: '123456789',
      siret: '12345678933333',
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(screen.getByText('Offerers screen')).toBeInTheDocument()
    })
  })

  it('should redirect to identification page if the offerer has no venue with the same siret', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        {
          id: 1,
          name: 'Venue Name 1',
          publicName: 'Venue Public Name 1',
          isPermanent: true,
        },
        {
          id: 2,
          name: 'Venue Name 2',
          publicName: 'Venue Public Name 2',
          isPermanent: true,
        },
      ],
    })
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue({
      location: null,
      apeCode: '75',
      isDiffusible: true,
      name: 'name',
      siren: '123456789',
      siret: '12345678933333',
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(screen.getByText('Authentication screen')).toBeInTheDocument()
    })
  })

  it('should display errors on api failure', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['api Error message'] }],
        } as ApiResult,
        ''
      )
    )
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    await waitFor(() => {
      expect(
        screen.getAllByText('Une erreur est survenue').length
      ).toBeGreaterThan(0)
    })
  })

  it('should render offerer form', async () => {
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Dites-nous pour quelle structure vous travaillez'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      ''
    )
  })

  it('should fill siret field only with numbers', async () => {
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      'AbdqsI'
    )

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      ''
    )
  })

  it('should render empty siret field error', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(screen.getByText('Continuer'))
    expect(
      await screen.findByText('Veuillez renseigner un SIRET')
    ).toBeInTheDocument()
  })

  it('should handle offererSiretData with null name', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue(
      structureDataBodyModelFactory({ name: null })
    )
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [],
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockSetOfferer).toHaveBeenCalledWith(
        expect.objectContaining({
          name: '',
        })
      )
    })
  })

  it('should handle offererSiretData with null apeCode', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue(
      structureDataBodyModelFactory({ apeCode: null })
    )
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [],
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockSetOfferer).toHaveBeenCalledWith(
        expect.objectContaining({
          apeCode: undefined,
        })
      )
    })
  })

  it('should handle ApiError with empty message in second try catch block', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: {},
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(
        screen.getAllByText('Une erreur est survenue').length
      ).toBeGreaterThan(0)
    })
  })

  it('should handle non-ApiError in second try catch block', async () => {
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValue(
      'string error'
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(
        screen.getAllByText(
          'Nous avons rencontré un problème lors de la récupération des données.'
        ).length
      ).toBeGreaterThan(0)
    })
  })
  it('should navigate to /hub when clicking previous button', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(
      await screen.findByRole('button', { name: 'Annuler et quitter' })
    )

    expect(screen.getByText('Hub screen')).toBeInTheDocument()
  })

  it('should clean storage, reset activity and clear isOpenToPublic when submitting a different siret while a siren is stored', async () => {
    const user = userEvent.setup()
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify({
        siret: '11111111111111',
        siren: '111111111',
        isOpenToPublic: true,
      })
    )
    inMemoryLocalStorage.set(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY, 'MUSEE')

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Tom Waits',
      offererSiren: '123456789',
      venues: [],
    })

    renderRealOffererScreen()

    const input = screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
    await user.clear(input)
    await user.type(input, '12345678933333')
    await user.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
    ).toBeUndefined()
    expect(cleanSignupJourneyStorage).toHaveBeenCalled()
    const newOfferer = JSON.parse(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) || '{}'
    )
    expect(newOfferer?.siret).toEqual('12345678933333')
    expect(newOfferer?.isOpenToPublic).toBeUndefined()
  })

  it('should NOT clean storage when submitting a different siret if no siren is stored', async () => {
    const user = userEvent.setup()
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify({ siret: '11111111111111', isOpenToPublic: true })
    )
    inMemoryLocalStorage.set(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY, 'MUSEE')

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Tom Waits',
      offererSiren: '123456789',
      venues: [],
    })

    renderRealOffererScreen()

    const input = screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
    await user.clear(input)
    await user.type(input, '12345678933333')
    await user.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
    ).toEqual('MUSEE')
    expect(cleanSignupJourneyStorage).not.toHaveBeenCalled()
    const newOfferer = JSON.parse(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) || '{}'
    )
    expect(newOfferer?.siret).toEqual('12345678933333')
    expect(newOfferer?.isOpenToPublic).toBe(true)
  })

  it('should immediately navigate to next step if the same siret with siren is already stored', async () => {
    const user = userEvent.setup()
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify({
        siret: '12345678933333',
        siren: '123456789',
        hasVenueWithSiret: false,
      })
    )
    const apiSpy = vi.spyOn(api, 'getVenuesOfOffererFromSiret')

    renderRealOffererScreen()

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      '12345678933333'
    )
    await user.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(apiSpy).not.toHaveBeenCalled()
    await waitFor(() => {
      expect(screen.getByText('Authentication screen')).toBeInTheDocument()
    })
  })

  it('should NOT immediately navigate if the same siret is stored but WITHOUT siren', async () => {
    const user = userEvent.setup()
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify({ siret: '12345678933333', hasVenueWithSiret: false })
    )
    const apiSpy = vi
      .spyOn(api, 'getVenuesOfOffererFromSiret')
      .mockResolvedValue({
        offererName: 'Tom Waits',
        offererSiren: '123456789',
        venues: [],
      })

    renderRealOffererScreen()

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      '12345678933333'
    )
    await user.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(apiSpy).toHaveBeenCalled()
    await waitFor(() => {
      expect(screen.getByText('Authentication screen')).toBeInTheDocument()
    })
  })

  it('should use siren from structure data if not provided by venues api', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue({
      ...structureDataBodyModelFactory(),
      siren: '987654321',
    })

    renderRealOffererScreen()

    const input = screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
    await user.clear(input)
    await user.type(input, '12345678933333')
    await user.click(screen.getByRole('button', { name: 'Continuer' }))

    const newOfferer = JSON.parse(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) || '{}'
    )
    expect(newOfferer?.siren).toEqual('987654321')
  })
})

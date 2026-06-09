import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api, apiNew } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import {
  SignupJourneyContext,
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
import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from '@/commons/utils/localStorageManager'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from './constants'
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
    cleanSignupJourneyStorage: vi.fn(),
    tryRestoreOffererFromStorage: vi.fn(),
    tryRestoreInitialAddressFromStorage: vi.fn(),
  }
})

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

const renderOffererScreenForRestoreFailure = (
  contextValue: SignupJourneyContextValues
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/identification"
            element={<Offerer />}
          />
          <Route
            path="/inscription/structure/recherche"
            element={<div>Search screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/identification'],
    }
  )
}

const mockSetOfferer = vi.fn()
const mockSetInitialAddress = vi.fn()

describe('Offerer', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    inMemoryLocalStorage.clear()
    vi.mocked(cleanSignupJourneyStorage).mockClear()
    vi.mocked(tryRestoreOffererFromStorage).mockReset()
    vi.mocked(tryRestoreInitialAddressFromStorage).mockReset()
    contextValue = {
      activity: null,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: mockSetOfferer,
      initialAddress: null,
      setInitialAddress: mockSetInitialAddress,
    }

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })

    vi.spyOn(apiNew, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
  })

  describe('Restore contexts from storage', () => {
    it('should try to restore offerer and initialAddress and reset the form when context is missing', async () => {
      const setOfferer = vi.fn()
      const setInitialAddress = vi.fn()
      contextValue.offerer = null
      contextValue.initialAddress = null
      contextValue.setOfferer = setOfferer
      contextValue.setInitialAddress = setInitialAddress

      const storedOfferer = {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '12345678933333',
      }
      vi.mocked(tryRestoreOffererFromStorage).mockReturnValue(storedOfferer)

      renderOffererScreen(contextValue)

      await waitFor(() => {
        expect(tryRestoreOffererFromStorage).toHaveBeenCalledWith(setOfferer)
        expect(tryRestoreInitialAddressFromStorage).toHaveBeenCalledWith(
          setInitialAddress
        )
      })
    })

    it('should try to restore offerer and initialAddress when context equals default values', async () => {
      const setOfferer = vi.fn()
      const setInitialAddress = vi.fn()
      contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
      contextValue.initialAddress = DEFAULT_ADDRESS_FORM_VALUES
      contextValue.setOfferer = setOfferer
      contextValue.setInitialAddress = setInitialAddress

      vi.mocked(tryRestoreOffererFromStorage).mockReturnValue({
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '12345678933333',
      })

      renderOffererScreen(contextValue)

      await waitFor(() => {
        expect(tryRestoreOffererFromStorage).toHaveBeenCalledWith(setOfferer)
        expect(tryRestoreInitialAddressFromStorage).toHaveBeenCalledWith(
          setInitialAddress
        )
      })
    })

    it('should clean storage and navigate to search when restoring offerer/address fails', async () => {
      contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
      contextValue.initialAddress = null
      vi.mocked(tryRestoreOffererFromStorage).mockImplementation(() => {
        throw new Error('ANY_ERROR')
      })

      renderOffererScreenForRestoreFailure(contextValue)

      await waitFor(() => {
        expect(cleanSignupJourneyStorage).toHaveBeenCalled()
        expect(screen.getByText('Search screen')).toBeInTheDocument()
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
    vi.spyOn(apiNew, 'getStructureData').mockRejectedValue(
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
          body: [{ error: ['API Error message'] }],
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
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
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
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
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
        screen.getByText(
          'Nous avons rencontré un problème lors de la récupération des données.'
        )
      ).toBeInTheDocument()
    })
  })
  it('should navigate to /hub when clicking previous button', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(
      await screen.findByRole('button', { name: 'Annuler et quitter' })
    )

    expect(screen.getByText('Hub screen')).toBeInTheDocument()
  })
})

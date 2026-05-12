import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import createFetchMock from 'vitest-fetch-mock'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from '@/commons/utils/localStorageManager'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { OffererAuthentication } from '../OffererAuthentication'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const inMemoryLocalStorage = new Map<string, string>()

const initialAddress = {
  ...DEFAULT_ADDRESS_FORM_VALUES,
  addressAutocomplete: '3 Rue de Valois 75001 Paris',
  'search-addressAutocomplete': '3 Rue de Valois 75001 Paris',
  street: '3 Rue de Valois',
  city: 'Paris',
  postalCode: '75001',
  inseeCode: '75111',
  latitude: 1.23,
  longitude: 2.34,
} as const

vi.mock('@/commons/context/SignupJourneyContext/storage', async () => {
  const actual = await vi.importActual(
    '@/commons/context/SignupJourneyContext/storage'
  )

  return {
    ...actual,
    cleanSignupJourneyStorage: vi.fn(),
    tryRestoreOffererFromStorage: vi.fn(),
    tryRestoreInitialAddressFromStorage: vi.fn(),
    tryRestoreActivityFromStorage: vi.fn(),
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
      <SnackBarContainer />
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
    inMemoryLocalStorage.clear()
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
      initialAddress,
      setInitialAddress: noop,
    }
  })

  describe('Restore contexts from storage', () => {
    it('should try to restore offerer and initialAddress when context is missing', async () => {
      const setOfferer = vi.fn()
      const setInitialAddress = vi.fn()
      contextValue.offerer = null
      contextValue.initialAddress = null
      contextValue.setOfferer = setOfferer
      contextValue.setInitialAddress = setInitialAddress

      vi.mocked(tryRestoreOffererFromStorage).mockReturnValue({
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '123 456 789 33333',
        name: 'Stored name',
        street: '1 Stored Street',
        postalCode: '75001',
        city: 'Paris',
      })

      renderOffererAuthenticationScreen(contextValue)

      await waitFor(() => {
        expect(tryRestoreOffererFromStorage).toHaveBeenCalledWith(setOfferer)
        expect(tryRestoreInitialAddressFromStorage).toHaveBeenCalledWith(
          setInitialAddress
        )
      })
    })

    it('should clean storage and navigate to offerer screen when restoring offerer/address fails', async () => {
      contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
      vi.mocked(tryRestoreOffererFromStorage).mockImplementation(() => {
        throw new Error('ANY_ERROR')
      })

      renderOffererAuthenticationScreen(contextValue)

      await waitFor(() => {
        expect(cleanSignupJourneyStorage).toHaveBeenCalled()
        expect(screen.getByText('Offerer screen')).toBeInTheDocument()
      })
      expect(tryRestoreActivityFromStorage).not.toHaveBeenCalled()
    })

    it('should try to restore activity and ignore restore errors', async () => {
      const setActivity = vi.fn()
      contextValue.activity = null
      contextValue.setActivity = setActivity
      contextValue.offerer = {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '123 456 789 33333',
        name: 'Test name',
        street: '3 Rue de Valois',
        city: 'Paris',
        postalCode: '75001',
        publicName: '',
        isOpenToPublic: 'true',
      }

      vi.mocked(tryRestoreActivityFromStorage).mockImplementation(() => {
        throw new Error('ANY_ERROR')
      })

      renderOffererAuthenticationScreen(contextValue)

      await waitFor(() => {
        expect(tryRestoreActivityFromStorage).toHaveBeenCalledWith(setActivity)
      })
      expect(
        screen.getByRole('heading', {
          level: 2,
          name: 'Complétez les informations de votre structure',
        })
      ).toBeInTheDocument()
    })
  })

  it('should render component', async () => {
    renderOffererAuthenticationScreen(contextValue)

    expect(
      await screen.findByText('Les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Retour' })).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Complétez les informations de votre structure',
      })
    ).toBeInTheDocument()

    expect(screen.getByText(/Numéro de SIRET/)).toBeInTheDocument()
    expect(screen.getByText('123 456 789 33333')).toBeInTheDocument()

    expect(screen.getByText(/Raison sociale/)).toBeInTheDocument()
    expect(screen.getByText('Test name')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()

    expect(screen.queryByRole('button', { name: 'Retour' })).toBeInTheDocument()
  })

  it('should render component with empty adresss', async () => {
    renderOffererAuthenticationScreen({
      ...contextValue,

      initialAddress: {
        ...DEFAULT_ADDRESS_FORM_VALUES,
        street: '123 Rue de Valois',
        city: 'Toto',
        postalCode: '123123',
      },
    })

    await waitFor(() => {
      expect(screen.getByLabelText(/Adresse postale/)).toHaveValue(
        '3 Rue de Valois 75001 Paris'
      )
    })
  })

  it('should display activity screen on submit', async () => {
    renderOffererAuthenticationScreen(contextValue)
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Complétez les informations de votre structure',
      })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
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
      initialAddress,
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

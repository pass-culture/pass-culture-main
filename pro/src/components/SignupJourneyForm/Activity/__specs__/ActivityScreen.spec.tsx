import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import type { SWRResponse } from 'swr'
import { vi } from 'vitest'

import { Target } from '@/apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import * as useEducationalDomains from '@/commons/hooks/swr/useEducationalDomains'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from '@/commons/utils/localStorageManager'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DEFAULT_ADDRESS_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { Activity } from '../Activity'

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
      clearPassCultureKeys: vi.fn(() => {
        inMemoryLocalStorage.clear()
      }),
    },
  }
})

vi.mock('@/apiClient/api', () => ({
  api: {
    listEducationalDomains: vi.fn(),
  },
}))

const renderActivityScreen = (
  contextValue: SignupJourneyContextValues,
  features: string[] = []
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/inscription/structure/activite"
            element={<Activity />}
          />
          <Route
            path="/inscription/structure/confirmation"
            element={<div>Validation screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/activite'],
      features,
    }
  )
}

describe('screens:SignupJourney::Activity', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    inMemoryLocalStorage.clear()
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: {
        name: 'Offerer Name',
        publicName: '',
        siret: '12345678933333',
        hasVenueWithSiret: false,
        isDiffusible: true,
        isOpenToPublic: 'true',
        ...DEFAULT_ADDRESS_FORM_VALUES,
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress,
      setInitialAddress: noop,
    }
  })

  it('should render component', async () => {
    contextValue.activity = null

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()
    expect(screen.getByLabelText(/Activité principale/)).toHaveValue('')
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter un lien' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      await screen.findByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: 'Étape précédente' })
    ).toBeInTheDocument()
  })

  it('should display validation screen on click next step button', async () => {
    contextValue.activity = {
      activity: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL_AND_EDUCATIONAL,
      phoneNumber: '0605120510',
      culturalDomains: undefined,
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    await waitFor(() => {
      expect(screen.getByText('Validation screen')).toBeInTheDocument()
    })
  })

  it('should go next step with individual target customer', async () => {
    contextValue.activity = {
      activity: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL,
      phoneNumber: '0605120510',
      culturalDomains: undefined,
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Au grand public')).toBeChecked()
    expect(screen.getByLabelText('À des groupes scolaires')).not.toBeChecked()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should go next step with educational target customer', async () => {
    contextValue.activity = {
      activity: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.EDUCATIONAL,
      phoneNumber: '0605120510',
      culturalDomains: undefined,
    }

    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Au grand public')).not.toBeChecked()
    expect(screen.getByLabelText('À des groupes scolaires')).toBeChecked()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should display authentification screen on click previous step button', async () => {
    renderActivityScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 2,
        name: 'Et enfin, définissez l’activité de votre structure',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape précédente' })
    )

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  describe('Cultural domains', () => {
    beforeEach(() => {
      contextValue.offerer = {
        name: 'test name',
        siret: '1234567893333',
        hasVenueWithSiret: false,
        isDiffusible: true,
        ...DEFAULT_ADDRESS_FORM_VALUES,
      }
      vi.spyOn(
        useEducationalDomains,
        'useEducationalDomains'
      ).mockImplementation(() => {
        return {
          isLoading: false,
          data: [
            {
              id: 1,
              name: 'domaine 1',
              nationalPrograms: [],
            },
            {
              id: 2,
              name: 'domaine b',
              nationalPrograms: [],
            },
            {
              id: 3,
              name: 'domaine III',
              nationalPrograms: [],
            },
          ],
        } as SWRResponse
      })
    })

    it('should render component with cultural domains required', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.isOpenToPublic = 'false'
      }
      renderActivityScreen(contextValue)
      expect(
        await screen.findByRole('heading', {
          level: 2,
          name: 'Et enfin, définissez l’activité de votre structure',
        })
      ).toBeInTheDocument()
      expect(screen.getByText(/Domaine\(s\) d’activité \*/)).toBeInTheDocument()
    })

    it('should render component with cultural domains NOT required', async () => {
      if (contextValue.offerer) {
        contextValue.offerer.isOpenToPublic = 'true'
      }
      renderActivityScreen(contextValue)
      expect(
        await screen.findByRole('heading', {
          level: 2,
          name: 'Et enfin, définissez l’activité de votre structure',
        })
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Domaine\(s\) d’activité \*/)
      ).not.toBeInTheDocument()
    })
  })
})

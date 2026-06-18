import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import type { ApiResult } from '@/apiClient/compat'
import type { VenueOfOffererFromSiretResponseModel } from '@/apiClient/v1'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from '@/commons/utils/localStorageManager'
import { noop } from '@/commons/utils/noop'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import * as storageAvailable from '@/commons/utils/storageAvailable'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'

import { ApiError, type ApiRequestOptions } from 'apiClient/compat'
import { Offerers } from '../Offerers'

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
    createOfferer: vi.fn(),
    getVenuesOfOffererFromSiret: vi.fn(),
    getOfferer: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))
vi.mock('@/commons/store/user/dispatchers/setSelectedOffererById', () => ({
  setSelectedOffererById: vi.fn(() => () => {
    const action = {
      type: 'user/setSelectedOffererById/fulfilled',
      payload: undefined,
    }

    const p: any = Promise.resolve(action)
    p.unwrap = () => Promise.resolve(action.payload)

    return p
  }),
}))

const renderOfferersScreen = async (
  contextValue: SignupJourneyContextValues,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Routes>
        <Route
          path="/inscription/structure/recherche"
          element={<div>Offerer screen</div>}
        />
        <Route
          path="/inscription/structure/recherche/rattachement"
          element={<Offerers />}
        />
        <Route
          path="/inscription/structure/identification"
          element={<div>Authentication screen</div>}
        />
        <Route
          path="/inscription/structure/rattachement/confirmation-rattachement"
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </SignupJourneyContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche/rattachement'],
      ...options,
    }
  )

  expect(await screen.findByText('Ce SIRET est déjà inscrit')).toBeVisible()
}
describe('screens:SignupJourney::Offerers', () => {
  let contextValue: SignupJourneyContextValues
  let venues: VenueOfOffererFromSiretResponseModel[]

  beforeEach(() => {
    inMemoryLocalStorage.clear()
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Offerer Name',
        siret: '12345678933333',
        apeCode: '5610C',
        city: 'lille',
        postalCode: '59000',
        siren: '123456789',
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress,
      setInitialAddress: noop,
    }

    venues = [
      {
        id: 0,
        siret: '12345678903333',
        name: 'Venue Name 0',
        publicName: 'Venue Public Name 0',
        isPermanent: false,
      },
      {
        id: 1,
        siret: null,
        name: 'Venue Name 1',
        publicName: 'Venue Public Name 1',
        isPermanent: true,
      },
      {
        id: 2,
        siret: null,
        name: 'Venue Name 2',
        publicName: 'Venue Public Name 2',
        isPermanent: true,
      },
      {
        id: 3,
        siret: null,
        name: 'Venue Name 3',
        publicName: 'Venue Public Name 3',
        isPermanent: true,
      },
    ]

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Offerer Name',
      offererSiren: '123456789',
      venues,
    })
  })

  it('should render component', async () => {
    await renderOfferersScreen(contextValue)
    expect(screen.getByText('Offerer Name')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', {
        name: 'Voir plus de structures',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Voir moins de structures',
      })
    ).not.toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Rejoindre cet espace' })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('button', {
        name: 'Retour à la recherche de SIRET',
      })
    ).toBeVisible()
  })

  it('should render component without venue creation', async () => {
    await renderOfferersScreen(contextValue)

    expect(
      await screen.findByRole('button', { name: 'Rejoindre cet espace' })
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).not.toBeInTheDocument()
  })

  it('should not display venues with sirets', async () => {
    await renderOfferersScreen(contextValue)

    expect(screen.queryByText('Venue Public Name 0')).not.toBeInTheDocument()
  })

  it('should not display "show more"', async () => {
    // toggle venues list is displayed only when venues length > 2
    venues.pop()
    await renderOfferersScreen(contextValue)

    expect(screen.getByText('Offerer Name')).toBeInTheDocument()

    expect(screen.getByText('Venue Public Name 2')).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher plus de structures',
      })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher moins de structures',
      })
    ).not.toBeInTheDocument()
  })

  it('should toggle venues list', async () => {
    await renderOfferersScreen(contextValue)

    expect(screen.queryByText('Venue Public Name 3')).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Voir plus de structures'))

    await waitFor(() => {
      expect(
        screen.queryByRole('button', {
          name: 'Voir plus de structures',
        })
      ).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', {
        name: 'Voir moins de structures',
      })
    ).toBeInTheDocument()

    expect(screen.queryByText('Venue Public Name 3')).toBeVisible()

    await userEvent.click(screen.getByText('Voir moins de structures'))

    expect(
      screen.getByRole('button', {
        name: 'Voir plus de structures',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Voir moins de structures',
      })
    ).not.toBeInTheDocument()
  })

  it('should redirect only local authority to offerer authentication on add offerer button click', async () => {
    const contextValueForLocalAuthority = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Trifoulli les Oies',
        siret: '12345678933333',
        apeCode: '8411Z',
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress,
      setInitialAddress: noop,
    }

    await renderOfferersScreen(contextValueForLocalAuthority)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    )

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should redirect to offerer on back button click', async () => {
    await renderOfferersScreen(contextValue)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Retour à la recherche de SIRET',
      })
    )

    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should display add a venue button for local authority', async () => {
    const contextValueForLocalAuthority = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Trifoulli les Oies',
        siret: '12345678933333',
        apeCode: '8411Z',
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress,
      setInitialAddress: noop,
    }

    await renderOfferersScreen(contextValueForLocalAuthority)
    expect(
      await screen.findByText('Ajouter une nouvelle structure')
    ).toBeInTheDocument()
  })

  describe('when WIP_PRE_SIGNUP_SIMULATION is enabled', () => {
    it('should display "Retour" button instead of ActionBar', async () => {
      await renderOfferersScreen(contextValue, {
        features: ['WIP_PRE_SIGNUP_SIMULATION'],
      })

      expect(screen.getByRole('link', { name: 'Retour' })).toBeVisible()

      expect(
        screen.queryByRole('button', {
          name: 'Retour à la recherche de SIRET',
        })
      ).not.toBeInTheDocument()
    })
  })

  describe('modal handling', () => {
    it('should display confirmation dialog when user want to be linked to the structure', async () => {
      await renderOfferersScreen(contextValue)

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText('Rejoindre cet espace ?')
      ).toBeInTheDocument()
    })

    it('should not link offerer to user when they cancel', async () => {
      await renderOfferersScreen(contextValue)

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText('Rejoindre cet espace ?')
      ).toBeInTheDocument()

      await userEvent.click(await screen.findByText('Annuler'))

      expect(
        screen.queryByText('Rejoindre cet espace ?')
      ).not.toBeInTheDocument()
      expect(api.createOfferer).not.toHaveBeenCalled()
    })

    it('should link offerer to user when they confirm', async () => {
      vi.spyOn(storageAvailable, 'storageAvailable').mockImplementation(
        () => false
      )
      await renderOfferersScreen(contextValue)
      vi.spyOn(api, 'createOfferer').mockResolvedValue(expect.anything())
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue(expect.anything())
      vi.spyOn(api, 'getOfferer').mockResolvedValue(expect.anything())

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText('Rejoindre cet espace ?')
      ).toBeInTheDocument()

      await userEvent.click(
        await screen.findByRole('button', { name: 'Rejoindre cet espace' })
      )

      expect(api.createOfferer).toHaveBeenCalledWith({
        body: {
          city: 'lille',
          name: 'Offerer Name',
          postalCode: '59000',
          siren: '123456789',
        },
      })
      expect(await screen.findByText('Confirmation screen')).toBeInTheDocument()
    })

    it('should display error message when createOfferer fails', async () => {
      const snackBarError = vi.fn()
      vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
        success: vi.fn(),
        error: snackBarError,
      }))

      vi.spyOn(storageAvailable, 'storageAvailable').mockImplementation(
        () => false
      )
      await renderOfferersScreen(contextValue)

      const apiError = new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {},
        } as ApiResult,
        ''
      )
      vi.spyOn(api, 'createOfferer').mockRejectedValueOnce(apiError)

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText('Rejoindre cet espace ?')
      ).toBeInTheDocument()

      await userEvent.click(
        await screen.findByRole('button', { name: 'Rejoindre cet espace' })
      )

      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith(
          'Impossible de lier votre compte à cette structure.'
        )
      })

      expect(screen.queryByText('Confirmation screen')).not.toBeInTheDocument()
    })
  })
})

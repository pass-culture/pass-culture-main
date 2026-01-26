import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { vi } from 'vitest'

import { AdageFrontRoles, type AuthenticatedResponse } from '@/apiClient/adage'
import { api } from '@/apiClient/api'
import { StudentLevels } from '@/apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  defaultUseInfiniteHitsReturn,
  defaultUseStatsReturn,
} from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { MAIN_INDEX_ID } from '../../OffersInstantSearch'
import { OffersSearch, type SearchProps } from '../OffersSearch'

interface getItems {
  objectID: string
  query: string
  popularity: number
  nb_words: number
}

const mockVenueSuggestions = [
  {
    objectID: '1',
    query: '',
    popularity: 1,
    nb_words: 1,
    label: 'Mock Venue 1',
    venue: {
      name: 'Mock Venue 1',
      publicName: 'Mock Venue 1',
    },
    offerer: {
      name: 'Mock Offerer 1',
    },
  },
  {
    objectID: '2',
    query: '',
    popularity: 1,
    nb_words: 1,
    label: 'Mock Venue 2',
    venue: {
      name: 'Mock Venue 2',
      publicName: 'Mock Venue 2',
    },
    offerer: {
      name: 'Mock Offerer 2',
    },
  },
]

const mockGetItems = vi.fn((): Array<getItems> => mockVenueSuggestions)
const mockSourceId = 'VenueSuggestionsSource'

vi.mock('@algolia/autocomplete-plugin-query-suggestions', () => {
  return {
    ...vi.importActual('@algolia/autocomplete-plugin-query-suggestions'),
    createQuerySuggestionsPlugin: vi.fn(() => {
      return {
        name: 'querySuggestionName',
        getSources: () => [
          {
            sourceId: mockSourceId,
            getItems: mockGetItems,
          },
        ],
      }
    }),
  }
})

vi.mock('../Offers/Offers', () => {
  return {
    Offers: vi.fn(() => <div />),
  }
})

vi.mock('@/apiClient/api', () => ({
  api: {
    listEducationalDomains: vi.fn(() => [
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
      { id: 3, name: 'Arts' },
    ]),
  },
  apiAdage: {
    getAcademies: vi.fn(() => ['Amiens', 'Paris']),
    logTrackingFilter: vi.fn(),
  },
}))

const renderOffersSearchComponent = (
  props: SearchProps,
  user: AuthenticatedResponse,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <>
      <AdageUserContextProvider adageUser={user}>
        <OffersSearch {...props} />
      </AdageUserContextProvider>
      <SnackBarContainer />
    </>,
    options
  )
}

const refineSearch = vi.fn()
const setGeoRadiusMock = vi.fn()

vi.mock('react-instantsearch', async () => {
  return {
    ...(await vi.importActual('react-instantsearch')),
    useSearchBox: () => ({ refine: refineSearch }),
    useInstantSearch: () => ({
      scopedResults: [
        {
          indexId: MAIN_INDEX_ID,
          results: {
            hits: [],
            nbHits: 0,
          },
        },
        {
          indexId: 'no_results_offers_index_0',
          results: {
            hits: defaultUseInfiniteHitsReturn.hits,
            nbHits: 1,
          },
        },
      ],
      refresh: vi.fn(),
    }),
    Configure: vi.fn(() => <div />),
    Index: vi.fn(({ children }) => children),
    useStats: () => ({
      ...defaultUseStatsReturn,
      nbHits: 0,
    }),
    useInfiniteHits: () => ({
      ...defaultUseInfiniteHitsReturn,
    }),
  }
})

describe('offersSearch component', () => {
  let props: SearchProps
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
    email: 'test@example.com',
    lat: 10,
    lon: 10,
  }
  const snackBarError = vi.fn()

  beforeEach(async () => {
    props = {
      setGeoRadius: setGeoRadiusMock,
      setFilters: () => {},
      initialFilters: {},
    }

    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))
  })

  it('should call algolia with requested query and uai all', async () => {
    // Given
    renderOffersSearchComponent(props, user)
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByRole('searchbox', { name: 'Rechercher' })
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(refineSearch).toHaveBeenCalledWith('Paris')
  })

  it('should call algolia with requested query and uai associatedToInstitution', async () => {
    // Given
    renderOffersSearchComponent(props, {
      ...user,
      uai: 'associatedToInstitution',
    })
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByRole('searchbox', { name: 'Rechercher' })
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(refineSearch).toHaveBeenCalledWith('Paris')
  })

  it('should display localisation filter with default state by default', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })

    // When
    const localisationFilter = screen.getByRole('button', {
      name: 'Localisation des partenaires',
    })
    await userEvent.click(localisationFilter)

    // Then
    expect(
      screen.getByText('Dans quelle zone géographique')
    ).toBeInTheDocument()
  })
  it('should display localisation filter with departments options if user has selected departement filter', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir un département'))
    await userEvent.click(
      screen.getByRole('checkbox', {
        name: '01 - Ain',
      })
    )
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires (1)',
      })
    )

    // Then
    expect(
      screen.getByRole('checkbox', { name: '01 - Ain' })
    ).toBeInTheDocument()
  })

  it('should display academies filter with departments options if user has selected academy filter', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir une académie'))
    await userEvent.click(
      screen.getByRole('checkbox', {
        name: 'Amiens',
      })
    )
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires (1)',
      })
    )

    // Then
    expect(screen.getByRole('checkbox', { name: 'Amiens' })).toBeInTheDocument()
  })

  it('should display radius input filter if user has selected around me filter', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(
      screen.getByText('Autour de mon établissement scolaire')
    )
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )

    // Then
    expect(setGeoRadiusMock).toHaveBeenCalled()
  })

  it('should not let user select the geoloc filter if they have an invalid location', async () => {
    renderOffersSearchComponent(props, {
      ...user,
      departmentCode: null,
      lat: 0,
      lon: null,
    })
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir une académie'))
    await userEvent.click(
      screen.getByRole('checkbox', {
        name: 'Amiens',
      })
    )
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )

    expect(setGeoRadiusMock).toHaveBeenCalledTimes(0)
  })

  it('should filters venue id on venue filter if provided', async () => {
    renderOffersSearchComponent(
      {
        ...props,
        initialFilters: {
          venue: {
            id: 1,
            name: 'Venue Name',
            publicName: 'Venue Public Name',
            relative: [],
            departementCode: '75',
          },
        },
      },
      user
    )

    const tagVenue = await screen.findByRole('button', {
      name: /Lieu : Venue Public Name/,
    })
    expect(tagVenue).toBeInTheDocument()
  })

  it('should filters with artistic domains id if provided in url', async () => {
    const mockLocation = {
      ...window.location,
      search: '?domain=1',
    }

    window.location = mockLocation as string & Location

    renderOffersSearchComponent(
      { ...props, initialFilters: { domains: [1] } },
      user
    )

    const tagDomain = await screen.findByRole('button', {
      name: /Danse/,
    })

    expect(tagDomain).toBeInTheDocument()
  })

  it('should go back to the localisation main menu when reopening the localisation multiselect after having submitted it with no values selected', async () => {
    renderOffersSearchComponent(props, user)

    const localisationFilter = screen.getByRole('button', {
      name: 'Localisation des partenaires',
    })
    await userEvent.click(localisationFilter)

    expect(
      screen.getByText('Dans quelle zone géographique')
    ).toBeInTheDocument()

    //  Open the departments submenu, thus set the localisation menu to department
    await userEvent.click(
      screen.getByRole('button', { name: 'Choisir un département' })
    )

    //  Submit without having selected anything
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )

    //  Reopen localisation filter
    await userEvent.click(localisationFilter)

    //  We see the location menu and not the departments list
    expect(
      screen.getByText('Dans quelle zone géographique')
    ).toBeInTheDocument()
  })

  it('should show an error message notification when domains could not be fetched', async () => {
    vi.spyOn(api, 'listEducationalDomains').mockRejectedValueOnce('error')

    renderOffersSearchComponent(props, user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(snackBarError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
  })

  it('should display suggestions if there are no search results', async () => {
    renderOffersSearchComponent(props, user)

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(screen.getByTestId('suggestions-header')).toBeInTheDocument()
  })

  it('should filter on student levels when the institution is in MeG and redirected from "/"', async () => {
    renderOffersSearchComponent(
      {
        ...props,
        initialFilters: {
          students: [
            StudentLevels._COLES_MARSEILLE_CP_CE1_CE2,
            StudentLevels._COLES_MARSEILLE_CM1_CM2,
            StudentLevels._COLES_MARSEILLE_MATERNELLE,
          ],
        },
      },
      {
        ...user,
      }
    )

    expect(
      await screen.findByRole('button', {
        name: /Écoles Marseille - Maternelle/,
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('button', {
        name: /Écoles Marseille - CP, CE1, CE2/,
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('button', {
        name: /Écoles Marseille - CM1, CM2/,
      })
    ).toBeInTheDocument()
  })
})

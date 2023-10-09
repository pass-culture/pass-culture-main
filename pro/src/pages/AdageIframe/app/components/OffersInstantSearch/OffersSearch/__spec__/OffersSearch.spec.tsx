import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import * as pcapi from 'pages/AdageIframe/repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersSearch, SearchProps } from '../OffersSearch'

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

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(() => ({
      categories: [],
      subcategories: [],
    })),
    getAcademies: vi.fn(() => ['Amiens', 'Paris']),
  },
}))

const isGeolocationActive = {
  features: {
    list: [
      {
        nameKey: 'WIP_ENABLE_ADAGE_GEO_LOCATION',
        isActive: true,
      },
    ],
    initialized: true,
  },
}

const renderOffersSearchComponent = (
  props: SearchProps,
  user: AuthenticatedResponse,
  storeOverrides?: unknown
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <OffersSearch {...props} />
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </AdageUserContextProvider>,
    { storeOverrides: storeOverrides }
  )
}

const refineSearch = vi.fn()
const setGeoRadiusMock = vi.fn()

vi.mock('react-instantsearch', async () => {
  return {
    ...((await vi.importActual('react-instantsearch')) ?? {}),
    useSearchBox: () => ({ refine: refineSearch }),
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

  beforeEach(() => {
    props = {
      venueFilter: null,
      setGeoRadius: setGeoRadiusMock,
    }
    vi.spyOn(pcapi, 'getEducationalDomains').mockResolvedValue([])
    vi.spyOn(apiAdage, 'getEducationalOffersCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))
  })

  it('should call algolia with requested query and uai all', async () => {
    // Given
    renderOffersSearchComponent(props, user)
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
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
    const textInput = screen.getByPlaceholderText(
      'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
    )
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(refineSearch).toHaveBeenCalledWith('Paris')
  })

  it('should display localisation filter with default state by default', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })
    await waitFor(() => {
      expect(pcapi.getEducationalDomains).toHaveBeenCalled()
    })

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
    await waitFor(() => {
      expect(pcapi.getEducationalDomains).toHaveBeenCalled()
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir un département'))
    await userEvent.click(
      screen.getByRole('option', {
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
      screen.getByPlaceholderText('Ex: 59 ou Hauts-de-France')
    ).toBeInTheDocument()
  })

  it('should display academies filter with departments options if user has selected academy filter', async () => {
    // Given
    renderOffersSearchComponent(props, { ...user, departmentCode: null })
    await waitFor(() => {
      expect(pcapi.getEducationalDomains).toHaveBeenCalled()
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir une académie'))
    await userEvent.click(
      screen.getByRole('option', {
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
    expect(screen.getByPlaceholderText('Ex: Nantes')).toBeInTheDocument()
  })

  it('should display radius input filter if user has selected around me filter', async () => {
    // Given
    renderOffersSearchComponent(
      props,
      { ...user, departmentCode: null },
      isGeolocationActive
    )
    await waitFor(() => {
      expect(pcapi.getEducationalDomains).toHaveBeenCalled()
    })

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
    renderOffersSearchComponent(
      props,
      { ...user, departmentCode: null, lat: 0, lon: null },
      isGeolocationActive
    )
    await waitFor(() => {
      expect(pcapi.getEducationalDomains).toHaveBeenCalled()
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(screen.getByText('Choisir une académie'))
    await userEvent.click(
      screen.getByRole('option', {
        name: 'Amiens',
      })
    )
    await userEvent.click(
      screen.getAllByRole('button', {
        name: 'Rechercher',
      })[1]
    )

    expect(setGeoRadiusMock).not.toHaveBeenCalled()
  })

  it('should filters department on venue filter if provided', async () => {
    renderOffersSearchComponent(
      {
        ...props,
        venueFilter: {
          id: 1,
          name: 'test',
          relative: [],
          departementCode: '75',
        },
      },
      user
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: /Localisation des partenaires/,
      })
    )
    expect(screen.getByLabelText('75 - Paris', { exact: false })).toBeChecked()
    expect(screen.getByLabelText('30 - Gard', { exact: false })).toBeChecked()
  })

  it('should go back to localisation main menu when reseting the localisation modal', async () => {
    renderOffersSearchComponent(props, user)

    await userEvent.click(
      screen.getByRole('button', {
        name: /Localisation des partenaires/,
      })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Réinitialiser' }))

    expect(
      screen.getByText('Dans quelle zone géographique')
    ).toBeInTheDocument()
  })

  it('should go back to the localisation main menu when reopening the localisation multiselect after having submitted it with no values selected', async () => {
    renderOffersSearchComponent(props, user)

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

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
})

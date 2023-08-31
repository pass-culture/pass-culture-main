import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import * as pcapi from 'pages/AdageIframe/repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersSearch, SearchProps } from '../OffersSearch'

vi.mock('../Offers/Offers', () => {
  return {
    Offers: vi.fn(() => <div />),
  }
})

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(),
    getAcademies: vi.fn(() => ['Amiens', 'Paris']),
  },
}))

jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: vi.fn(),
}))

jest.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: vi.fn().mockReturnValue(true),
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
    <AdageUserContext.Provider value={{ adageUser: user }}>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <OffersSearch {...props} />
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </AdageUserContext.Provider>,
    { storeOverrides: storeOverrides }
  )
}

const refineSearch = vi.fn()
const refineGeoloc = vi.fn()

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
      setGeoLocation: refineGeoloc,
    }
    vi.spyOn(pcapi, 'getEducationalDomains').mockResolvedValue([])
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))

    vi.mock('react-instantsearch-dom', async () => {
      return {
        ...((await vi.importActual('react-instantsearch-dom')) ?? {}),
        Configure: vi.fn(() => <div />),
        connectSearchBox: vi
          .fn()
          .mockImplementation(Component => (props: SearchBoxProvided) => (
            <Component {...props} refine={refineSearch} />
          )),
      }
    })
  })

  it('should call algolia with requested query and uai all', async () => {
    // Given
    renderOffersSearchComponent(props, user)
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
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
      'Rechercher : nom de l’offre, partenaire culturel'
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
    expect(refineGeoloc).toHaveBeenCalled()
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

    expect(refineGeoloc).not.toHaveBeenCalled()
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
})

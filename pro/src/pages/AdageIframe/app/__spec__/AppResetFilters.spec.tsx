import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'
import type { Mock } from 'vitest'

import { AdageFrontRoles, VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from '../providers'
import { FeaturesContextProvider } from '../providers/FeaturesContextProvider'

vi.mock('react-instantsearch-dom', async () => {
  const actual = await vi.importActual('react-instantsearch-dom')
  return {
    ...(actual as object),
    Configure: vi.fn(() => <div />),
    connectStats: vi.fn(Component => (props: any) => (
      <Component
        {...props}
        areHitsSorted={false}
        nbHits={0}
        nbSortedHits={0}
        processingTimeMS={0}
      />
    )),
  }
})

vi.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: vi.fn().mockResolvedValue([
    { id: 1, name: 'Danse' },
    { id: 2, name: 'Architecture' },
  ]),
  getFeatures: vi.fn().mockResolvedValue([]),
}))

vi.mock('apiClient/api', () => ({
  apiAdage: {
    authenticate: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getEducationalOffersCategories: vi.fn().mockResolvedValue({
      categories: [
        { id: 'CINEMA', proLabel: 'Cinéma' },
        { id: 'MUSEE', proLabel: 'Musée' },
      ],
      subcategories: [
        {
          id: 'CINE_PLEIN_AIR',
          proLabel: 'Cinéma plein air',
          categoryId: 'CINEMA',
        },
        {
          id: 'EVENEMENT_CINE',
          proLabel: 'Évènement cinéma',
          categoryId: 'CINEMA',
        },
        {
          id: 'VISITE_GUIDEE',
          proLabel: 'Visite guidée',
          categoryId: 'MUSEE',
        },
        {
          id: 'VISITE',
          proLabel: 'Visite',
          categoryId: 'MUSEE',
        },
      ],
    }),
    getVenueById: vi.fn(),
    getVenueBySiret: vi.fn(),
    logCatalogView: vi.fn(),
    logSearchButtonClick: vi.fn(),
  },
}))

vi.mock('utils/config', async () => {
  const actual = await vi.importActual('utils/config')
  return {
    ...(actual as object),
    ALGOLIA_API_KEY: 'adage-api-key',
    ALGOLIA_APP_ID: '1',
    ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
  }
})

const renderApp = () => {
  renderWithProviders(
    <FiltersContextProvider>
      <FeaturesContextProvider>
        <AlgoliaQueryContextProvider>
          <FacetFiltersContextProvider>
            <App />
          </FacetFiltersContextProvider>
        </AlgoliaQueryContextProvider>
      </FeaturesContextProvider>
    </FiltersContextProvider>
  )
}

describe('app', () => {
  let venue: VenueResponse

  beforeEach(() => {
    global.window = Object.create(window)
    const url = 'https://www.example.com'
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
        search: '',
      },
    })

    venue = {
      id: 1436,
      name: 'Librairie de Paris',
      publicName: "Lib de Par's",
      relative: [],
    }

    vi.spyOn(apiAdage, 'authenticate').mockResolvedValue({
      role: AdageFrontRoles.REDACTOR,
      uai: 'uai',
    })
    vi.spyOn(apiAdage, 'getVenueBySiret').mockResolvedValue(venue)
    vi.spyOn(apiAdage, 'getVenueById').mockResolvedValue(venue)
  })

  it('should reset filters', async () => {
    renderApp()

    const departmentFilter = await screen.findByLabelText('Département')
    const studentsFilter = await screen.findByLabelText('Niveau scolaire')
    const categoriesFilter = await screen.findByLabelText('Catégorie')
    const domainsFilter = await screen.findByLabelText('Domaine')
    const launchSearchButton = await screen.findByRole('button', {
      name: 'Lancer la recherche',
    })

    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('59 - Nord'))

    await userEvent.click(studentsFilter)
    await userEvent.click(screen.getByText('Collège - 4e'))

    await userEvent.click(domainsFilter)
    await userEvent.click(screen.getByText('Danse'))

    await userEvent.click(categoriesFilter)
    await userEvent.click(screen.getByText('Cinéma'))

    await userEvent.click(launchSearchButton)

    const resetFiltersButton = screen.queryByRole('button', {
      name: 'Réinitialiser les filtres',
    }) as HTMLElement

    // When
    await waitFor(() =>
      expect(
        screen.queryByRole('button', { name: '01 - Ain' })
      ).toBeInTheDocument()
    )
    await userEvent.click(resetFiltersButton)
    await userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(3))

    const searchConfigurationLastCall = (Configure as Mock).mock.calls[2][0]
    expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    expect(
      screen.queryByRole('button', { name: '01 - Ain' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: '59 - Nord' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Collège - 4e' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Danse' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Cinéma' })
    ).not.toBeInTheDocument()
  })

  it('should reset all filters and launch search when no result and click on button', async () => {
    // Given
    renderApp()

    const textInput = await screen.findByPlaceholderText(
      'Nom de l’offre ou du partenaire culturel'
    )
    const departmentFilter = await screen.findByLabelText('Département')
    const launchSearchButton = await screen.findByRole('button', {
      name: 'Lancer la recherche',
    })

    // When
    await userEvent.type(textInput, 'a')
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))

    await userEvent.click(launchSearchButton)

    expect(screen.queryByRole('button', { name: 'a' })).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: '01 - Ain' })
    ).toBeInTheDocument()

    const resetAllFiltersButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    await userEvent.click(resetAllFiltersButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(3))
    const searchConfigurationFirstCall = (Configure as Mock).mock.calls[1][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      ['venue.departmentCode:01', 'offer.interventionArea:01'],
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    const searchConfigurationLastCall = (Configure as Mock).mock.calls[2][0]
    expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    expect(screen.queryByRole('button', { name: 'a' })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: '01 - Ain' })
    ).not.toBeInTheDocument()
  })

  it('should display a "Réinitialiser les filtres" button when no result query is not empty', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce('')
    renderApp()
    const searchBox = await screen.findByPlaceholderText(
      'Nom de l’offre ou du partenaire culturel'
    )
    const launchSearchButton = await screen.findByRole('button', {
      name: 'Lancer la recherche',
    })

    await userEvent.type(searchBox, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    const resetFiltersNoResultButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).toBeInTheDocument()
  })

  it('should display a "Réinitialiser les filtres" button when no result and at least one filter is set', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce('')
    renderApp()

    // When
    const departmentFilter = await screen.findByLabelText('Département')
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))
    const launchSearchButton = await screen.findByRole('button', {
      name: 'Lancer la recherche',
    })
    await userEvent.click(launchSearchButton)

    // Then
    const resetFiltersNoResultButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).toBeInTheDocument()
  })
})

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'
import selectEvent from 'react-select-event'

import { api } from 'api/api'
import { AdageFrontRoles, VenueResponse } from 'api/gen'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from 'app/providers'
import { FeaturesContextProvider } from 'app/providers/FeaturesContextProvider'

import { App } from '../App'

import {
  findCategoriesFilter,
  findDepartmentFilter,
  findDomainsFilter,
  findLaunchSearchButton,
  findResetAllFiltersButton,
  findSearchBox,
  findStudentsFilter,
  queryResetFiltersButton,
  queryTag,
} from './__test_utils__/elements'

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    Configure: jest.fn(() => <div />),
  }
})

jest.mock('repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn().mockResolvedValue([
    { id: 1, name: 'Danse' },
    { id: 2, name: 'Architecture' },
  ]),
  getFeatures: jest.fn().mockResolvedValue([
    { name: 'ENABLE_EDUCATIONAL_DOMAINS', isActive: true },
    { name: 'ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION', isActive: true },
  ]),
}))

jest.mock('api/api', () => ({
  api: {
    getAdageIframeAuthenticate: jest.fn(),
    getAdageIframeGetVenueById: jest.fn(),
    getAdageIframeGetVenueBySiret: jest.fn(),
    getAdageIframeGetEducationalOffersCategories: jest.fn().mockResolvedValue({
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
          proLabel: 'Événement cinéma',
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
    getAdageIframeGetCollectiveOffer: jest.fn(),
  },
}))
const mockedApi = api as jest.Mocked<typeof api>

const renderApp = () => {
  render(
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
    const url = 'http://www.example.com'
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
    }

    mockedApi.getAdageIframeAuthenticate.mockResolvedValue({
      role: AdageFrontRoles.Redactor,
      uai: 'uai',
    })
    mockedApi.getAdageIframeGetVenueBySiret.mockResolvedValue(venue)
    mockedApi.getAdageIframeGetVenueById.mockResolvedValue(venue)
  })

  it('should reset filters', async () => {
    const siret = '123456789'
    window.location.search = `?siret=${siret}`
    renderApp()

    const departmentFilter = await findDepartmentFilter()
    const studentsFilter = await findStudentsFilter()
    const categoriesFilter = await findCategoriesFilter()
    const domainsFilter = await findDomainsFilter()
    const launchSearchButton = await findLaunchSearchButton()

    await selectEvent.select(departmentFilter, '01 - Ain')
    await selectEvent.select(departmentFilter, '59 - Nord')
    await selectEvent.select(studentsFilter, 'Collège - 4e')
    await selectEvent.select(domainsFilter, 'Danse')
    await selectEvent.select(categoriesFilter, 'Cinéma')
    userEvent.click(launchSearchButton)

    const resetFiltersButton = queryResetFiltersButton() as HTMLElement

    // When
    userEvent.click(resetFiltersButton)
    userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(5))
    const searchConfigurationLastCall = (Configure as jest.Mock).mock
      .calls[4][0]
    expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    expect(queryTag('01 - Ain')).not.toBeInTheDocument()
    expect(queryTag('59 - Nord')).not.toBeInTheDocument()
    expect(queryTag('Collège - 4e')).not.toBeInTheDocument()
    expect(queryTag('Danse')).not.toBeInTheDocument()
    expect(queryTag('Cinéma')).not.toBeInTheDocument()
    expect(queryTag(`Lieu : ${venue?.publicName}`)).not.toBeInTheDocument()
  })

  it('should reset all filters and launch search when no result and click on button', async () => {
    // Given
    const siret = '123456789'
    window.location.search = `?siret=${siret}`
    renderApp()

    const textInput = await findSearchBox()
    const departmentFilter = await findDepartmentFilter()
    const launchSearchButton = await findLaunchSearchButton()

    // When
    userEvent.type(textInput, 'a')
    await selectEvent.select(departmentFilter, '01 - Ain')
    userEvent.click(launchSearchButton)

    expect(queryTag('a')).toBeInTheDocument()
    expect(queryTag('01 - Ain')).toBeInTheDocument()

    const resetAllFiltersButton = await findResetAllFiltersButton()
    userEvent.click(resetAllFiltersButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(4))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      ['venue.departmentCode:01'],
      'venue.id:1436',
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    const searchConfigurationLastCall = (Configure as jest.Mock).mock
      .calls[3][0]
    expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    expect(queryTag('a')).not.toBeInTheDocument()
    expect(queryTag('01 - Ain')).not.toBeInTheDocument()
  })

  it('should display a "Réinitialiser les filtres" button when no result query is not empty', async () => {
    // Given
    mockedApi.getAdageIframeGetCollectiveOffer.mockRejectedValue('')
    renderApp()
    const searchBox = await findSearchBox()
    const launchSearchButton = await findLaunchSearchButton()

    userEvent.type(searchBox, 'Paris')
    userEvent.click(launchSearchButton)

    // Then
    const resetFiltersNoResultButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).toBeInTheDocument()
  })

  it('should display a "Réinitialiser les filtres" button when no result and at least one filter is set', async () => {
    // Given
    mockedApi.getAdageIframeGetCollectiveOffer.mockRejectedValue('')
    renderApp()

    // When
    const departmentFilter = await findDepartmentFilter()
    await selectEvent.select(departmentFilter, '01 - Ain')
    const launchSearchButton = await findLaunchSearchButton()
    userEvent.click(launchSearchButton)

    // Then
    const resetFiltersNoResultButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).toBeInTheDocument()
  })

  it('should not display a "Réinitialiser les filtres" button when there is no query and no filters', async () => {
    // Given
    mockedApi.getAdageIframeGetCollectiveOffer.mockRejectedValue('')
    renderApp()

    // Then
    const resetFiltersNoResultButton = screen.queryByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).not.toBeInTheDocument()
  })
})

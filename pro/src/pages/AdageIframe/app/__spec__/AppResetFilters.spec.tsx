import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import { AdageFrontRoles, VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'

import { App } from '../App'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from '../providers'
import { FeaturesContextProvider } from '../providers/FeaturesContextProvider'

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
    connectStats: jest.fn(Component => (props: any) => (
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

jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn().mockResolvedValue([
    { id: 1, name: 'Danse' },
    { id: 2, name: 'Architecture' },
  ]),
  getFeatures: jest.fn().mockResolvedValue([]),
}))

jest.mock('apiClient/api', () => ({
  apiAdage: {
    authenticate: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getEducationalOffersCategories: jest.fn().mockResolvedValue({
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
    getVenueById: jest.fn(),
    getVenueBySiret: jest.fn(),
    logCatalogView: jest.fn(),
    logSearchButtonClick: jest.fn(),
  },
}))

jest.mock('utils/config', () => ({
  ALGOLIA_API_KEY: 'adage-api-key',
  ALGOLIA_APP_ID: '1',
  ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
}))

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
      relative: [],
    }

    jest.spyOn(apiAdage, 'authenticate').mockResolvedValue({
      role: AdageFrontRoles.REDACTOR,
      uai: 'uai',
    })
    jest.spyOn(apiAdage, 'getVenueBySiret').mockResolvedValue(venue)
    jest.spyOn(apiAdage, 'getVenueById').mockResolvedValue(venue)
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

    userEvent.click(launchSearchButton)

    const resetFiltersButton = queryResetFiltersButton() as HTMLElement

    // When
    await waitFor(() => expect(queryTag('01 - Ain')).toBeInTheDocument())
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
    await userEvent.type(textInput, 'a')
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))

    await userEvent.click(launchSearchButton)

    expect(queryTag('a')).toBeInTheDocument()
    expect(queryTag('01 - Ain')).toBeInTheDocument()

    const resetAllFiltersButton = await findResetAllFiltersButton()
    userEvent.click(resetAllFiltersButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(4))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      ['venue.departmentCode:01', 'offer.interventionArea:01'],
      ['venue.id:1436'],
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
    jest.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce('')
    renderApp()
    const searchBox = await findSearchBox()
    const launchSearchButton = await findLaunchSearchButton()

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
    jest.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce('')
    renderApp()

    // When
    const departmentFilter = await findDepartmentFilter()
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))
    const launchSearchButton = await findLaunchSearchButton()
    userEvent.click(launchSearchButton)

    // Then
    const resetFiltersNoResultButton = await screen.findByRole('button', {
      name: 'Réinitialiser tous les filtres',
    })
    expect(resetFiltersNoResultButton).toBeInTheDocument()
  })
})

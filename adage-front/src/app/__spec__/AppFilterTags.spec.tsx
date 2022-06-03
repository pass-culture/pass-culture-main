import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'
import selectEvent from 'react-select-event'

import { api } from 'api/api'
import { AdageFrontRoles } from 'api/gen'
import {
  FiltersContextProvider,
  FacetFiltersContextProvider,
  AlgoliaQueryContextProvider,
} from 'app/providers'
import { FeaturesContextProvider } from 'app/providers/FeaturesContextProvider'
import { VenueFilterType } from 'app/types/offers'
import * as pcapi from 'repository/pcapi/pcapi'

import { App } from '../App'

import {
  findCategoriesFilter,
  findDepartmentFilter,
  findDomainsFilter,
  findLaunchSearchButton,
  findSearchBox,
  findStudentsFilter,
  queryResetFiltersButton,
  queryTag,
} from './__test_utils__/elements'

jest.mock('utils/config', () => ({
  ALGOLIA_APP_ID: 'algolia-app-id',
  ALGOLIA_API_KEY: 'algolia-api-key',
  ALGOLIA_OFFERS_INDEX: 'algolia-index-name',
}))

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    Configure: jest.fn(() => <div />),
  }
})

jest.mock('repository/pcapi/pcapi', () => ({
  getVenueBySiret: jest.fn(),
  getVenueById: jest.fn(),
  getEducationalCategories: jest.fn().mockResolvedValue({
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
  getEducationalDomains: jest.fn().mockResolvedValue([
    { id: 1, name: 'Danse' },
    { id: 2, name: 'Architecture' },
  ]),
  getFeatures: jest
    .fn()
    .mockResolvedValue([
      { name: 'ENABLE_EDUCATIONAL_DOMAINS', isActive: true },
    ]),
}))
const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

jest.mock('api/api', () => ({
  api: { getAdageIframeAuthenticate: jest.fn() },
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
  let venue: VenueFilterType

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
    })
    mockedPcapi.getVenueBySiret.mockResolvedValue(venue)
    mockedPcapi.getVenueById.mockResolvedValue(venue)
  })

  it('should display filter tags and send selected filters to Algolia', async () => {
    window.location.search = ''
    // Given
    renderApp()

    const departmentFilter = await findDepartmentFilter()
    const studentsFilter = await findStudentsFilter()
    const categoriesFilter = await findCategoriesFilter()
    const domainsFilter = await findDomainsFilter()
    const launchSearchButton = await findLaunchSearchButton()

    // When
    await selectEvent.select(departmentFilter, '01 - Ain')
    userEvent.click(launchSearchButton)
    await selectEvent.select(departmentFilter, '59 - Nord')
    await selectEvent.select(studentsFilter, 'Collège - 4e')
    await selectEvent.select(categoriesFilter, 'Cinéma')
    await selectEvent.select(domainsFilter, 'Danse')
    await selectEvent.select(categoriesFilter, 'Musée')
    userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(3))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[1][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      'offer.isEducational:true',
      ['venue.departmentCode:01'],
    ])
    const searchConfigurationSecondCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
      'offer.isEducational:true',
      ['venue.departmentCode:01', 'venue.departmentCode:59'],
      [
        'offer.subcategoryId:CINE_PLEIN_AIR',
        'offer.subcategoryId:EVENEMENT_CINE',
        'offer.subcategoryId:VISITE_GUIDEE',
        'offer.subcategoryId:VISITE',
      ],
      ['offer.students:Collège - 4e'],
      ['offer.domains:1'],
    ])

    expect(queryTag('01 - Ain')).toBeInTheDocument()
    expect(queryTag('59 - Nord')).toBeInTheDocument()
    expect(queryTag('Collège - 4e')).toBeInTheDocument()
    expect(queryTag('Danse')).toBeInTheDocument()
    expect(queryTag('Cinéma')).toBeInTheDocument()
    expect(queryTag('Musée')).toBeInTheDocument()
  })

  it('should remove deselected departments and students from filters sent to Algolia', async () => {
    // Given
    renderApp()

    const departmentFilter = await findDepartmentFilter()
    const studentsFilter = await findStudentsFilter()
    const launchSearchButton = await findLaunchSearchButton()

    await selectEvent.select(departmentFilter, '01 - Ain')
    await selectEvent.select(departmentFilter, '59 - Nord')
    await selectEvent.select(studentsFilter, 'Collège - 4e')

    // When
    userEvent.click(launchSearchButton)
    await selectEvent.select(departmentFilter, '01 - Ain')
    userEvent.click(launchSearchButton)
    await selectEvent.select(departmentFilter, '59 - Nord')
    await selectEvent.select(studentsFilter, 'Collège - 4e')
    userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(4))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[1][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      'offer.isEducational:true',
      ['venue.departmentCode:01', 'venue.departmentCode:59'],
      ['offer.students:Collège - 4e'],
    ])
    const searchConfigurationSecondCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
      'offer.isEducational:true',
      ['venue.departmentCode:59'],
      ['offer.students:Collège - 4e'],
    ])
    const searchConfigurationThirdCall = (Configure as jest.Mock).mock
      .calls[3][0]
    expect(searchConfigurationThirdCall.facetFilters).toStrictEqual([
      'offer.isEducational:true',
    ])

    expect(queryTag('01 - Ain')).not.toBeInTheDocument()
    expect(queryTag('59 - Nord')).not.toBeInTheDocument()
    expect(queryTag('Collège - 4e')).not.toBeInTheDocument()
  })

  it('should remove filter when clicking on delete button', async () => {
    // Given
    renderApp()

    // When
    const departmentFilter = await findDepartmentFilter()
    await selectEvent.select(departmentFilter, '01 - Ain')

    const filterTag = screen.getByText('01 - Ain', { selector: 'div' })
    expect(filterTag).toBeInTheDocument()

    const closeIcon = filterTag.lastChild

    await waitFor(() => fireEvent.click(closeIcon as ChildNode))

    // Then
    expect(
      screen.queryByText('01 - Ain', { selector: 'div' })
    ).not.toBeInTheDocument()
  })

  it('should display tag with query after clicking on search button', async () => {
    renderApp()
    const textInput = await findSearchBox()
    const launchSearchButton = await findLaunchSearchButton()

    userEvent.type(textInput, 'blabla')

    expect(queryTag('blabla')).not.toBeInTheDocument()

    userEvent.click(launchSearchButton)

    const resetFiltersButton = queryResetFiltersButton() as HTMLElement

    expect(queryTag('blabla')).toBeInTheDocument()
    expect(resetFiltersButton).toBeInTheDocument()
  })
})

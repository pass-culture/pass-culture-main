import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import { AdageFrontRoles, VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from '../providers'
import {
  FeaturesContext,
  FeaturesContextType,
} from '../providers/FeaturesContextProvider'

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

jest.mock('utils/config', () => ({
  ALGOLIA_API_KEY: 'adage-api-key',
  ALGOLIA_APP_ID: '1',
  ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
}))
jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn().mockResolvedValue([
    { id: 1, name: 'Danse' },
    { id: 2, name: 'Architecture' },
  ]),
  getFeatures: jest.fn().mockResolvedValue([]),
}))

jest.mock('apiClient/api', () => ({
  apiAdage: {
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
    authenticate: jest.fn(),
    getVenueBySiret: jest.fn(),
    logCatalogView: jest.fn(),
    logSearchButtonClick: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

const mockedApi = apiAdage as jest.Mocked<typeof apiAdage>
const features: FeaturesContextType = []

const renderApp = () => {
  renderWithProviders(
    <FiltersContextProvider>
      <FeaturesContext.Provider value={features}>
        <AlgoliaQueryContextProvider>
          <FacetFiltersContextProvider>
            <App />
          </FacetFiltersContextProvider>
        </AlgoliaQueryContextProvider>
      </FeaturesContext.Provider>
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
    mockedApi.getVenueBySiret.mockResolvedValue(venue)
    mockedApi.getVenueById.mockResolvedValue(venue)
  })

  it('should display filter tags and send selected filters to Algolia', async () => {
    window.location.search = ''
    // Given
    renderApp()
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    const departmentFilter = screen.getByLabelText('Département')
    const studentsFilter = screen.getByLabelText('Niveau scolaire')
    const categoriesFilter = screen.getByLabelText('Catégorie')
    const domainsFilter = screen.getByLabelText('Domaine')
    const launchSearchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })

    // when
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))
    await userEvent.click(launchSearchButton)

    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('59 - Nord'))

    await userEvent.click(studentsFilter)
    await userEvent.click(screen.getByText('Collège - 4e'))
    await userEvent.click(categoriesFilter)
    await userEvent.click(screen.getByText('Cinéma'))
    await userEvent.click(domainsFilter)
    await userEvent.click(screen.getByText('Danse'))
    await userEvent.click(categoriesFilter)
    await userEvent.click(screen.getByText('Musée'))
    await userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(3))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[1][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      ['venue.departmentCode:01', 'offer.interventionArea:01'],
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    const searchConfigurationSecondCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
      [
        'venue.departmentCode:01',
        'offer.interventionArea:01',
        'venue.departmentCode:59',
        'offer.interventionArea:59',
      ],
      [
        'offer.subcategoryId:CINE_PLEIN_AIR',
        'offer.subcategoryId:EVENEMENT_CINE',
        'offer.subcategoryId:VISITE_GUIDEE',
        'offer.subcategoryId:VISITE',
      ],
      ['offer.students:Collège - 4e'],
      ['offer.domains:1'],
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])

    expect(screen.getByRole('button', { name: '01 - Ain' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: '59 - Nord' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Collège - 4e' })
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Danse' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cinéma' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Musée' })).toBeInTheDocument()
  })

  it('should remove deselected departments and students from filters sent to Algolia', async () => {
    // Given
    renderApp()
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    const departmentFilter = screen.getByLabelText('Département')
    const studentsFilter = screen.getByLabelText('Niveau scolaire')
    const launchSearchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })

    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('59 - Nord'))
    await userEvent.click(studentsFilter)
    await userEvent.click(screen.getByText('Collège - 4e'))

    // When
    await userEvent.click(launchSearchButton)
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getAllByText('01 - Ain')[0])
    await userEvent.click(launchSearchButton)
    await userEvent.click(screen.getByRole('button', { name: '59 - Nord' }))
    await userEvent.click(screen.getByRole('button', { name: 'Collège - 4e' }))
    await userEvent.click(launchSearchButton)

    // Then
    await waitFor(() => expect(Configure).toHaveBeenCalledTimes(4))
    const searchConfigurationFirstCall = (Configure as jest.Mock).mock
      .calls[1][0]
    expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
      [
        'venue.departmentCode:01',
        'offer.interventionArea:01',
        'venue.departmentCode:59',
        'offer.interventionArea:59',
      ],
      ['offer.students:Collège - 4e'],
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    const searchConfigurationSecondCall = (Configure as jest.Mock).mock
      .calls[2][0]
    expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
      ['venue.departmentCode:59', 'offer.interventionArea:59'],
      ['offer.students:Collège - 4e'],
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:uai',
      ],
    ])
    const searchConfigurationThirdCall = (Configure as jest.Mock).mock
      .calls[3][0]
    expect(searchConfigurationThirdCall.facetFilters).toStrictEqual([
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
  })

  it('should remove filter when clicking on delete button', async () => {
    // Given
    renderApp()
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    // When
    const departmentFilter = screen.getByLabelText('Département')
    await userEvent.click(departmentFilter)
    await userEvent.click(screen.getByText('01 - Ain'))

    const filterTag = screen.getByRole('button', { name: '01 - Ain' })
    expect(filterTag).toBeInTheDocument()

    await userEvent.click(filterTag)

    // Then
    expect(
      screen.queryByText('01 - Ain', { selector: 'div' })
    ).not.toBeInTheDocument()
  })

  it('should display tag with query after clicking on search button', async () => {
    renderApp()
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    const textInput = screen.getByPlaceholderText(
      'Nom de l’offre ou du partenaire culturel'
    )
    const launchSearchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })

    await userEvent.type(textInput, 'blabla')

    expect(
      screen.queryByRole('button', { name: 'blablabla' })
    ).not.toBeInTheDocument()

    await userEvent.click(launchSearchButton)

    const resetFiltersButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })

    expect(screen.getByRole('button', { name: 'blabla' })).toBeInTheDocument()
    expect(resetFiltersButton).toBeInTheDocument()
  })
})

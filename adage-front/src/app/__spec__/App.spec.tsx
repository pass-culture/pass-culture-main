import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import { AdageFrontRoles, VenueResponse } from 'apiClient'
import { api } from 'apiClient/api'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from 'app/providers'
import { FeaturesContext } from 'app/providers/FeaturesContextProvider'

import { App } from '../App'

import {
  findLaunchSearchButton,
  queryResetFiltersButton,
  queryTag,
} from './__test_utils__/elements'

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    Configure: jest.fn(() => <div />),
    // eslint-disable-next-line react/display-name
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

jest.mock('apiClient/api', () => ({
  api: {
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
    getVenueById: jest.fn(),
    authenticate: jest.fn(),
    getVenueBySiret: jest.fn(),
    logSearchButtonClick: jest.fn(),
    logCatalogView: jest.fn(),
  },
}))

const mockedApi = api as jest.Mocked<typeof api>

const features = []

const renderApp = () => {
  render(
    <FiltersContextProvider>
      <AlgoliaQueryContextProvider>
        <FacetFiltersContextProvider>
          <FeaturesContext.Provider value={features}>
            <App />
          </FeaturesContext.Provider>
        </FacetFiltersContextProvider>
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>
  )
}

describe('app', () => {
  describe('when is authenticated', () => {
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

      mockedApi.authenticate.mockResolvedValue({
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
      })
      mockedApi.getVenueBySiret.mockResolvedValue(venue)
      mockedApi.getVenueById.mockResolvedValue(venue)
    })

    it('should show search offers input with no filter on venue when no siret or venueId is provided', async () => {
      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
      expect(Configure).toHaveBeenCalledTimes(1)

      expect(queryResetFiltersButton()).not.toBeInTheDocument()
      expect(
        screen.queryByText('Lieu :', { exact: false })
      ).not.toBeInTheDocument()

      expect(mockedApi.getVenueBySiret).not.toHaveBeenCalled()
    })

    it('should show search offers input with filter on venue public name when siret is provided and public name exists', async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}`

      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      expect(Configure).toHaveBeenCalledTimes(2)
      const searchConfiguration = (Configure as jest.Mock).mock.calls[1][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        `venue.id:${venue.id}`,
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])

      expect(queryTag(`Lieu : ${venue?.publicName}`)).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()

      expect(mockedApi.getVenueBySiret).toHaveBeenCalledWith(siret)
    })

    it('should show venue filter on venue name when siret is provided and public name does not exist', async () => {
      // Given
      const siret = '123456789'
      venue.publicName = undefined
      window.location.search = `?siret=${siret}`

      // When
      renderApp()

      // Then
      const venueFilter = await screen.findByText(`Lieu : ${venue.name}`)
      expect(venueFilter).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()
    })

    it('should show search offers input with filter on venue public name when venueId is provided and public name exists', async () => {
      // Given
      const venueId = 123456789
      window.location.search = `?venue=${venueId}`

      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      expect(Configure).toHaveBeenCalledTimes(2)
      const searchConfiguration = (Configure as jest.Mock).mock.calls[1][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        `venue.id:${venue.id}`,
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])

      expect(queryTag(`Lieu : ${venue?.publicName}`)).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()

      expect(mockedApi.getVenueById).toHaveBeenCalledWith(venueId)
    })

    it('should show venue filter on venue name when venueId is provided and public name does not exist', async () => {
      // Given
      const venueId = '123456789'
      venue.publicName = undefined
      window.location.search = `?venue=${venueId}`

      // When
      renderApp()

      // Then
      const venueFilter = await screen.findByText(`Lieu : ${venue.name}`)
      expect(venueFilter).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()
    })

    it("should show search offers input with no filter when venue isn't recognized", async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}`
      mockedApi.getVenueBySiret.mockRejectedValue('Unrecognized SIRET')

      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
      expect(Configure).toHaveBeenCalledTimes(1)
      expect(queryTag(`Lieu : ${venue?.publicName}`)).not.toBeInTheDocument()
      expect(queryResetFiltersButton()).not.toBeInTheDocument()
      expect(
        screen.getByText('Lieu inconnu. Tous les résultats sont affichés.')
      ).toBeInTheDocument()
    })

    it('should remove venue filter on click', async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}`

      renderApp()

      const venueFilter = await screen.findByText(`Lieu : ${venue?.publicName}`)
      const removeFilterButton = within(venueFilter).getByRole('button')
      const launchSearchButton = await findLaunchSearchButton()

      // When
      userEvent.click(removeFilterButton)
      userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(4))
      const searchConfigurationFirstCall = (Configure as jest.Mock).mock
        .calls[2][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        `venue.id:${venue.id}`,
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
      expect(queryTag(`Lieu : ${venue?.publicName}`)).not.toBeInTheDocument()
      expect(queryResetFiltersButton()).not.toBeInTheDocument()
    })

    describe('tabs', () => {
      it('should display tabs if user has UAI code', async () => {
        // Given
        renderApp()

        const firstTab = await screen.findByText('Toutes les offres')
        const secondTab = await screen.findByText(
          'Partagé avec mon établissement'
        )

        expect(firstTab).toBeInTheDocument()
        expect(secondTab).toBeInTheDocument()
      })

      it('should not display tabs if user does not have UAI code', async () => {
        // Given
        mockedApi.authenticate.mockResolvedValueOnce({
          role: AdageFrontRoles.REDACTOR,
          uai: null,
        })
        renderApp()

        // wait that app is rendered
        await screen.findByText('Rechercher une offre', {
          selector: 'h2',
        })

        const firstTab = screen.queryByText('Toutes les offres')
        const secondTab = screen.queryByText('Partagé avec mon établissement')

        expect(firstTab).not.toBeInTheDocument()
        expect(secondTab).not.toBeInTheDocument()
      })

      it('should add a facet filter when user clicks on "Partagé avec mon établissement"', async () => {
        // Given
        renderApp()

        const secondTab = await screen.findByText(
          'Partagé avec mon établissement'
        )
        userEvent.click(secondTab)

        const searchConfigurationSecondCall = (Configure as jest.Mock).mock
          .calls[2][0]

        expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
          `venue.id:${venue.id}`,
          ['offer.educationalInstitutionUAICode:uai'],
        ])
      })
    })
  })

  describe('when is not authenticated', () => {
    beforeEach(() => {
      mockedApi.authenticate.mockRejectedValue('Authentication failed')
    })

    it('should show error page', async () => {
      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText(
        'Une erreur s’est produite.',
        { selector: 'h1' }
      )
      expect(contentTitle).toBeInTheDocument()
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    })
  })
})

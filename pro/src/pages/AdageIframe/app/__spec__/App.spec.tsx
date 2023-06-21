import { screen, waitFor } from '@testing-library/react'
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

jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn(),
  getFeatures: jest.fn(),
}))

jest.mock('utils/config', () => ({
  ALGOLIA_API_KEY: 'adage-api-key',
  ALGOLIA_APP_ID: '1',
  ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
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
    logSearchButtonClick: jest.fn(),
    logCatalogView: jest.fn(),
    getCollectiveOffer: jest.fn(),
  },
}))

const features: FeaturesContextType = []

const renderApp = (venueFilter: VenueResponse | null) => {
  renderWithProviders(
    <FiltersContextProvider venueFilter={venueFilter}>
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

      jest.spyOn(apiAdage, 'authenticate').mockResolvedValue({
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
        departmentCode: '30',
        institutionName: 'COLLEGE BELLEVUE',
        institutionCity: 'ALES',
      })
      jest.spyOn(apiAdage, 'getVenueBySiret').mockResolvedValue(venue)
      jest.spyOn(apiAdage, 'getVenueById').mockResolvedValue(venue)
    })

    it('should show search offers input with no filter on venue when no siret or venueId is provided', async () => {
      // When
      renderApp(venue)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        ['venue.departmentCode:30'],
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
      expect(Configure).toHaveBeenCalledTimes(1)

      expect(
        screen.queryByText('Lieu :', { exact: false })
      ).not.toBeInTheDocument()

      expect(apiAdage.getVenueBySiret).not.toHaveBeenCalled()
    })

    it('should show search offers input with filter on venue public name when siret is provided and public name exists', async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}`

      // When
      renderApp(venue)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()

      await waitFor(() => {
        expect(Configure).toHaveBeenCalledTimes(1)
      })
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        [`venue.id:${venue.id}`],
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])

      expect(apiAdage.getVenueBySiret).toHaveBeenCalledWith(siret, false)
    })

    it('should show venue filter on venue name when siret is provided and public name does not exist', async () => {
      // Given
      const siret = '123456789'
      venue.publicName = undefined
      window.location.search = `?siret=${siret}`

      // When
      renderApp(venue)

      // Then
      const venueFilter = await screen.findByText(`Lieu : ${venue.name}`)
      expect(apiAdage.getVenueBySiret).toHaveBeenCalledWith(siret, false)
      expect(venueFilter).toBeInTheDocument()
    })

    it('should show search offers input with filter on venue public name when venueId is provided and public name exists', async () => {
      // Given
      const venueId = 123456789
      window.location.search = `?venue=${venueId}`

      // When
      renderApp(venue)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()

      await waitFor(() => {
        expect(Configure).toHaveBeenCalledTimes(1)
      })
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        [`venue.id:${venue.id}`],
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])

      expect(apiAdage.getVenueById).toHaveBeenCalledWith(venueId, false)
    })

    it('should show venue filter on venue name when venueId is provided and public name does not exist', async () => {
      // Given
      const venueId = 123456789
      venue.publicName = undefined
      window.location.search = `?venue=${venueId}`

      // When
      renderApp(venue)

      // Then
      const venueFilter = await screen.findByText(`Lieu : ${venue.name}`)
      expect(apiAdage.getVenueById).toHaveBeenCalledWith(venueId, false)
      expect(venueFilter).toBeInTheDocument()
    })

    it("should show search offers input with no filter when venue isn't recognized", async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}`
      jest
        .spyOn(apiAdage, 'getVenueBySiret')
        .mockRejectedValue('Unrecognized SIRET')

      // When
      renderApp(venue)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      expect(apiAdage.getVenueBySiret).toHaveBeenCalledWith(siret, false)
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        ['venue.departmentCode:30'],
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
      expect(Configure).toHaveBeenCalledTimes(1)
      expect(
        screen.queryByRole('button', { name: `Lieu : ${venue?.publicName}` })
      ).not.toBeInTheDocument()
      expect(
        await screen.findByText(
          'Lieu inconnu. Tous les résultats sont affichés.'
        )
      ).toBeInTheDocument()
    })

    it('should add all related venues in facet filters when siret is provided and "all" query param is true', async () => {
      // Given
      const siret = '123456789'
      window.location.search = `?siret=${siret}&all=true`
      jest.spyOn(apiAdage, 'getVenueBySiret').mockResolvedValueOnce({
        ...venue,
        relative: [123, 456],
      })

      // When
      renderApp(venue)

      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      expect(apiAdage.getVenueBySiret).toHaveBeenCalledWith(siret, true)

      await waitFor(() => {
        const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
        expect(searchConfiguration.facetFilters).toStrictEqual([
          [`venue.id:${venue.id}`, 'venue.id:123', 'venue.id:456'],
          [
            'offer.educationalInstitutionUAICode:all',
            'offer.educationalInstitutionUAICode:uai',
          ],
        ])
      })
    })

    it('should add all related venues in facet filters when venue is provided and "all" query param is true', async () => {
      // Given
      window.location.search = `?venue=${venue.id}&all=true`
      jest.spyOn(apiAdage, 'getVenueById').mockResolvedValueOnce({
        ...venue,
        relative: [123, 456],
      })

      // When
      renderApp(venue)

      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()

      expect(apiAdage.getVenueById).toHaveBeenCalledWith(venue.id, true)

      await waitFor(() => {
        const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
        expect(searchConfiguration.facetFilters).toStrictEqual([
          [`venue.id:${venue.id}`, 'venue.id:123', 'venue.id:456'],
          [
            'offer.educationalInstitutionUAICode:all',
            'offer.educationalInstitutionUAICode:uai',
          ],
        ])
      })
    })

    it('should remove venue filter on click', async () => {
      // Given
      window.location.search = `?venue=${venue.id}&all=true`

      renderApp(venue)

      const venueFilter = await screen.findByText(`Lieu : ${venue?.publicName}`)
      const launchSearchButton = screen.getByRole('button', {
        name: 'Lancer la recherche',
      })

      // When
      await userEvent.click(venueFilter)
      await userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(3))
      const searchConfigurationCall = (Configure as jest.Mock).mock.calls[2][0]

      expect(searchConfigurationCall.facetFilters).toStrictEqual([
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
      expect(
        screen.queryByRole('button', { name: `Lieu : ${venue?.publicName}` })
      ).not.toBeInTheDocument()
    })

    it('should uncheck on department only and search on intervention area also when only in my department is unchecked', async () => {
      window.location.search = ''
      renderApp(null)

      const onlyInMyDptFilter = await screen.findByLabelText(
        'Les acteurs culturels de mon département : ALES (30)'
      )
      const launchSearchButton = screen.getByRole('button', {
        name: 'Lancer la recherche',
      })
      // When
      await userEvent.click(onlyInMyDptFilter)
      await userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(2))
      const searchConfigurationFirstCall = (Configure as jest.Mock).mock
        .calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        ['venue.departmentCode:30', 'offer.interventionArea:30'],
        [
          'offer.educationalInstitutionUAICode:all',
          'offer.educationalInstitutionUAICode:uai',
        ],
      ])
    })

    describe('tabs', () => {
      it('should display tabs if user has UAI code', async () => {
        const siret = '123456789'
        window.location.search = `?siret=${siret}`
        // Given
        renderApp(venue)

        const firstTab = await screen.findByText('Toutes les offres')
        const secondTab = await screen.findByText(
          'Partagé avec mon établissement'
        )

        expect(firstTab).toBeInTheDocument()
        expect(secondTab).toBeInTheDocument()
      })

      it('should not display tabs if user does not have UAI code', async () => {
        // Given
        jest.spyOn(apiAdage, 'authenticate').mockResolvedValueOnce({
          role: AdageFrontRoles.REDACTOR,
          uai: null,
        })
        renderApp(venue)

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
        renderApp(venue)

        const secondTab = await screen.findByText(
          'Partagé avec mon établissement'
        )
        await userEvent.click(secondTab)

        expect(Configure).toHaveBeenNthCalledWith(
          2,

          expect.objectContaining({
            facetFilters: [
              ['venue.id:1436'],
              ['offer.educationalInstitutionUAICode:uai'],
            ],
          }),
          {}
        )
      })
    })
  })

  describe('when is not authenticated', () => {
    beforeEach(() => {
      jest
        .spyOn(apiAdage, 'authenticate')
        .mockRejectedValue('Authentication failed')
    })

    it('should show error page', async () => {
      // When
      renderApp(null)

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

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import { api } from 'api/api'
import { AdageFrontRoles } from 'api/gen'
import {
  FiltersContextProvider,
  FacetFiltersContextProvider,
  AlgoliaQueryContextProvider,
} from 'app/providers'
import { VenueFilterType } from 'app/types/offers'
import * as pcapi from 'repository/pcapi/pcapi'

import { App } from '../App'

import {
  findLaunchSearchButton,
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
}))
const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

jest.mock('api/api', () => ({
  api: {
    getAdageIframeAuthenticate: jest.fn(),
  },
}))
const mockedApi = api as jest.Mocked<typeof api>

const renderApp = () => {
  render(
    <FiltersContextProvider>
      <AlgoliaQueryContextProvider>
        <FacetFiltersContextProvider>
          <App />
        </FacetFiltersContextProvider>
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>
  )
}

describe('app', () => {
  describe('when is authenticated', () => {
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
        'offer.isEducational:true',
      ])
      expect(Configure).toHaveBeenCalledTimes(1)

      expect(queryResetFiltersButton()).not.toBeInTheDocument()
      expect(
        screen.queryByText('Lieu :', { exact: false })
      ).not.toBeInTheDocument()

      expect(mockedPcapi.getVenueBySiret).not.toHaveBeenCalled()
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
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      expect(queryTag(`Lieu : ${venue?.publicName}`)).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()

      expect(mockedPcapi.getVenueBySiret).toHaveBeenCalledWith(siret)
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
      const venueId = '123456789'
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
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      expect(queryTag(`Lieu : ${venue?.publicName}`)).toBeInTheDocument()
      expect(queryResetFiltersButton()).toBeInTheDocument()

      expect(mockedPcapi.getVenueById).toHaveBeenCalledWith(venueId)
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
      mockedPcapi.getVenueBySiret.mockRejectedValue('Unrecognized SIRET')

      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = (Configure as jest.Mock).mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        'offer.isEducational:true',
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
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      const searchConfigurationLastCall = (Configure as jest.Mock).mock
        .calls[3][0]
      expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(queryTag(`Lieu : ${venue?.publicName}`)).not.toBeInTheDocument()
      expect(queryResetFiltersButton()).not.toBeInTheDocument()
    })
  })

  describe('when is not authenticated', () => {
    beforeEach(() => {
      mockedApi.getAdageIframeAuthenticate.mockRejectedValue(
        'Authentication failed'
      )
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

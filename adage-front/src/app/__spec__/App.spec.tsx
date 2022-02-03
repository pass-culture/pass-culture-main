import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'
import selectEvent from 'react-select-event'

import * as pcapi from 'repository/pcapi/pcapi'
import { Role, VenueFilterType } from 'utils/types'

import { App } from '../App'

import {
  findCategoriesFilter,
  findDepartmentFilter,
  findLaunchSearchButton,
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
  authenticate: jest.fn(),
  getVenueBySiret: jest.fn(),
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

      mockedPcapi.authenticate.mockResolvedValue(Role.redactor)
      mockedPcapi.getVenueBySiret.mockResolvedValue(venue)
    })

    it('should show search offers input with no filter on venue when no siret is provided', async () => {
      // When
      render(<App />)

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
      render(<App />)

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
      render(<App />)

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
      render(<App />)

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

      render(<App />)

      const venueFilter = await screen.findByText(`Lieu : ${venue?.publicName}`)
      const removeFilterButton = within(venueFilter).getByRole('button')
      const launchSearchButton = await findLaunchSearchButton()

      // When
      userEvent.click(removeFilterButton)
      userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(5))
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

    it('should send selected filters to Algolia', async () => {
      window.location.search = ''
      // Given
      render(<App />)

      const departmentFilter = await findDepartmentFilter()
      const studentsFilter = await findStudentsFilter()
      const categoriesFilter = await findCategoriesFilter()
      const launchSearchButton = await findLaunchSearchButton()

      // When
      await selectEvent.select(departmentFilter, '01 - Ain')
      userEvent.click(launchSearchButton)
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(studentsFilter, 'Collège - 4e')
      await selectEvent.select(categoriesFilter, 'Cinéma')
      await selectEvent.select(categoriesFilter, 'Musée')
      userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(5))
      const searchConfigurationFirstCall = (Configure as jest.Mock).mock
        .calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01'],
      ])
      const searchConfigurationSecondCall = (Configure as jest.Mock).mock
        .calls[3][0]
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
      ])

      expect(queryTag('01 - Ain')).toBeInTheDocument()
      expect(queryTag('59 - Nord')).toBeInTheDocument()
      expect(queryTag('Collège - 4e')).toBeInTheDocument()
      expect(queryTag('Cinéma')).toBeInTheDocument()
      expect(queryTag('Musée')).toBeInTheDocument()
    })

    it('should remove deselected departments and students from filters sent to Algolia', async () => {
      // Given
      render(<App />)

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
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(7))
      const searchConfigurationFirstCall = (Configure as jest.Mock).mock
        .calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01', 'venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationSecondCall = (Configure as jest.Mock).mock
        .calls[4][0]
      expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationThirdCall = (Configure as jest.Mock).mock
        .calls[6][0]
      expect(searchConfigurationThirdCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])

      expect(queryTag('01 - Ain')).not.toBeInTheDocument()
      expect(queryTag('59 - Nord')).not.toBeInTheDocument()
      expect(queryTag('Collège - 4e')).not.toBeInTheDocument()
    })

    it('should reset filters', async () => {
      render(<App />)

      const departmentFilter = await findDepartmentFilter()
      const studentsFilter = await findStudentsFilter()
      const categoriesFilter = await findCategoriesFilter()
      const launchSearchButton = await findLaunchSearchButton()

      await selectEvent.select(departmentFilter, '01 - Ain')
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(studentsFilter, 'Collège - 4e')
      await selectEvent.select(categoriesFilter, 'Cinéma')
      userEvent.click(launchSearchButton)

      const resetFiltersButton = queryResetFiltersButton() as HTMLElement

      // When
      userEvent.click(resetFiltersButton)
      userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(Configure).toHaveBeenCalledTimes(5))
      const searchConfigurationFirstCall = (Configure as jest.Mock).mock
        .calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01', 'venue.departmentCode:59'],
        [
          'offer.subcategoryId:CINE_PLEIN_AIR',
          'offer.subcategoryId:EVENEMENT_CINE',
        ],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationLastCall = (Configure as jest.Mock).mock
        .calls[4][0]
      expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(queryTag('01 - Ain')).not.toBeInTheDocument()
      expect(queryTag('59 - Nord')).not.toBeInTheDocument()
      expect(queryTag('Collège - 4e')).not.toBeInTheDocument()
      expect(queryTag('Cinéma')).not.toBeInTheDocument()
    })
  })

  describe('when is not authenticated', () => {
    beforeEach(() => {
      mockedPcapi.authenticate.mockRejectedValue('Authentication failed')
    })

    it('should show error page', async () => {
      // When
      render(<App />)

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

import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'
import selectEvent from 'react-select-event'

import * as pcapi from 'repository/pcapi/pcapi'
import { Role, VenueFilterType } from 'utils/types'

import { App } from '../App'

import {
  getResetFiltersButton,
  getStudentsFilter,
  getDepartmentFilter,
  getLaunchSearchButton,
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
}))
const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

describe('app', () => {
  describe('when is authenticated', () => {
    let venue: VenueFilterType

    beforeEach(() => {
      Reflect.deleteProperty(global.window, 'location')
      window.location = new URL('https://www.example.com')

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
      const searchConfiguration = Configure.mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(Configure).toHaveBeenCalledTimes(1)

      expect(getResetFiltersButton()).not.toBeInTheDocument()
      expect(
        screen.queryByText('Lieu :', { exact: false })
      ).not.toBeInTheDocument()

      expect(mockedPcapi.getVenueBySiret).not.toHaveBeenCalled()
    })

    it('should show search offers input with filter on venue public name when siret is provided and public name exists', async () => {
      // Given
      const siret = '123456789'
      Reflect.deleteProperty(global.window, 'location')
      window.location = new URL(`https://www.example.com?siret=${siret}`)

      // When
      render(<App />)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      expect(Configure).toHaveBeenCalledTimes(2)
      const searchConfiguration = Configure.mock.calls[1][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      expect(
        screen.getByText(`Lieu : ${venue?.publicName}`)
      ).toBeInTheDocument()
      expect(getResetFiltersButton()).toBeInTheDocument()

      expect(mockedPcapi.getVenueBySiret).toHaveBeenCalledWith(siret)
    })

    it('should show venue filter on venue name when siret is provided and public name does not exist', async () => {
      // Given
      const siret = '123456789'
      venue.publicName = undefined
      Reflect.deleteProperty(global.window, 'location')
      window.location = new URL(`https://www.example.com?siret=${siret}`)

      // When
      render(<App />)

      // Then
      const venueFilter = await screen.findByText(`Lieu : ${venue.name}`)
      expect(venueFilter).toBeInTheDocument()
      expect(getResetFiltersButton()).toBeInTheDocument()
    })

    it("should show search offers input with no filter when venue isn't recognized", async () => {
      // Given
      const siret = '123456789'
      Reflect.deleteProperty(global.window, 'location')
      window.location = new URL(`https://www.example.com?siret=${siret}`)
      mockedPcapi.getVenueBySiret.mockRejectedValue('Unrecognized SIRET')

      // When
      render(<App />)

      // Then
      const contentTitle = await screen.findByText('Rechercher une offre', {
        selector: 'h2',
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = Configure.mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(Configure).toHaveBeenCalledTimes(1)
      expect(
        screen.queryByText(`Lieu : ${venue?.publicName}`)
      ).not.toBeInTheDocument()
      expect(getResetFiltersButton()).not.toBeInTheDocument()
      expect(
        screen.getByText('Lieu inconnu. Tous les résultats sont affichés.')
      ).toBeInTheDocument()
    })

    it('should remove venue filter on click', async () => {
      // Given
      const siret = '123456789'
      Reflect.deleteProperty(global.window, 'location')
      window.location = new URL(`https://www.example.com?siret=${siret}`)
      render(<App />)

      const venueFilter = await screen.findByText(`Lieu : ${venue?.publicName}`)
      const removeFilterButton = within(venueFilter).getByRole('button')
      const launchSearchButton = await getLaunchSearchButton()

      // When
      fireEvent.click(removeFilterButton)
      fireEvent.click(launchSearchButton)

      // Then
      expect(Configure).toHaveBeenCalledTimes(5)
      const searchConfigurationFirstCall = Configure.mock.calls[2][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      const searchConfigurationLastCall = Configure.mock.calls[3][0]
      expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(
        screen.queryByText(`Lieu : ${venue?.publicName}`)
      ).not.toBeInTheDocument()
      expect(getResetFiltersButton()).not.toBeInTheDocument()
    })

    it('should send selected departments and students as filters to Algolia', async () => {
      // Given
      render(<App />)

      const departmentFilter = await getDepartmentFilter()
      const launchSearchButton = await getLaunchSearchButton()

      // When
      await selectEvent.select(departmentFilter, '01 - Ain')
      fireEvent.click(launchSearchButton)
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(await getStudentsFilter(), 'Collège - 4e')
      fireEvent.click(launchSearchButton)

      // Then
      expect(Configure).toHaveBeenCalledTimes(5)
      const searchConfigurationFirstCall = Configure.mock.calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01'],
      ])
      const searchConfigurationSecondCall = Configure.mock.calls[3][0]
      expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01', 'venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])

      expect(
        screen.queryByText('01 - Ain', { selector: 'div' }) // use selector div otherwise the option is found
      ).toBeInTheDocument()
      expect(
        screen.queryByText('59 - Nord', { selector: 'div' }) // use selector div otherwise the option is found
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Collège - 4e', { selector: 'div' }) // use selector div otherwise the option is found
      ).toBeInTheDocument()
    })

    it('should remove deselected departments and students from filters sent to Algolia', async () => {
      // Given
      render(<App />)

      const departmentFilter = await getDepartmentFilter()
      const studentsFilter = await getStudentsFilter()
      const launchSearchButton = await getLaunchSearchButton()

      await selectEvent.select(departmentFilter, '01 - Ain')
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(studentsFilter, 'Collège - 4e')

      // When
      fireEvent.click(launchSearchButton)
      await selectEvent.select(departmentFilter, '01 - Ain')
      fireEvent.click(launchSearchButton)
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(studentsFilter, 'Collège - 4e')
      fireEvent.click(launchSearchButton)

      // Then
      expect(Configure).toHaveBeenCalledTimes(7)
      const searchConfigurationFirstCall = Configure.mock.calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01', 'venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationSecondCall = Configure.mock.calls[4][0]
      expect(searchConfigurationSecondCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationThirdCall = Configure.mock.calls[6][0]
      expect(searchConfigurationThirdCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])

      expect(
        screen.queryByText('01 - Ain', { selector: 'div' }) // use selector div otherwise the option is found
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('59 - Nord', { selector: 'div' }) // use selector div otherwise the option is found
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Collège - 4e', { selector: 'div' }) // use selector div otherwise the option is found
      ).not.toBeInTheDocument()
    })

    it('should reset filters', async () => {
      render(<App />)

      const departmentFilter = await getDepartmentFilter()
      const studentsFilter = await getStudentsFilter()
      const launchSearchButton = await getLaunchSearchButton()

      await selectEvent.select(departmentFilter, '01 - Ain')
      await selectEvent.select(departmentFilter, '59 - Nord')
      await selectEvent.select(studentsFilter, 'Collège - 4e')
      fireEvent.click(launchSearchButton)

      const resetFiltersButton = getResetFiltersButton() as HTMLElement

      // When
      await waitFor(() => fireEvent.click(resetFiltersButton))
      fireEvent.click(launchSearchButton)

      // Then
      expect(Configure).toHaveBeenCalledTimes(5)
      const searchConfigurationFirstCall = Configure.mock.calls[1][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        ['venue.departmentCode:01', 'venue.departmentCode:59'],
        ['offer.students:Collège - 4e'],
      ])
      const searchConfigurationLastCall = Configure.mock.calls[4][0]
      expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(
        screen.queryByText('01 - Ain', { selector: 'div' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('59 - Nord', { selector: 'div' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Collège - 4e', { selector: 'div' })
      ).not.toBeInTheDocument()
    })

    it('should disable Lancer La Recherche button when app is fetching offers', async () => {
      // Given
      render(<App />)
      const launchSearchButton = await getLaunchSearchButton()

      // When
      userEvent.click(launchSearchButton)

      // Then
      await waitFor(() => expect(launchSearchButton).toBeDisabled())
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

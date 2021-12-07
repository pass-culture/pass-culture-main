import { fireEvent, render, screen, within } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import { Role, VenueFilterType } from 'utils/types'

import { App } from '../App'

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
      expect(screen.queryByText('Lieu filtré :')).not.toBeInTheDocument()
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
      const searchConfiguration = Configure.mock.calls[0][0]
      expect(searchConfiguration.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])
      expect(Configure).toHaveBeenCalledTimes(1)
      expect(screen.getByText('Lieu filtré :')).toBeInTheDocument()
      expect(screen.getByText(venue.publicName as string)).toBeInTheDocument()
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
      const venueFilter = await screen.findByText(venue.name)
      expect(venueFilter).toBeInTheDocument()
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
      expect(screen.queryByText('Lieu filtré :')).not.toBeInTheDocument()
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

      const venueFilter = await screen.findByText('Lieu filtré :')
      const removeFilterButton = within(venueFilter.closest('div')).getByRole(
        'button'
      )

      // When
      fireEvent.click(removeFilterButton)

      // Then
      const searchConfigurationFirstCall = Configure.mock.calls[0][0]
      expect(searchConfigurationFirstCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
        `venue.id:${venue.id}`,
      ])

      const searchConfigurationLastCall = Configure.mock.calls[1][0]
      expect(searchConfigurationLastCall.facetFilters).toStrictEqual([
        'offer.isEducational:true',
      ])
      expect(Configure).toHaveBeenCalledTimes(2)
      expect(screen.queryByText('Lieu filtré :')).not.toBeInTheDocument()
      expect(screen.queryByText(venue.name)).not.toBeInTheDocument()
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

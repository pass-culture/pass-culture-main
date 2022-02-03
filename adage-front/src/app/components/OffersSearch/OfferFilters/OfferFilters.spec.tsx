import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import selectEvent from 'react-select-event'

import { VenueFilterType } from 'utils/types'

import { OfferFilters } from './OfferFilters'

jest.mock('repository/pcapi/pcapi', () => ({
  authenticate: jest.fn(),
  getVenueBySiret: jest.fn(),
}))

describe('offerFilters', () => {
  describe('filter tags', () => {
    let venue: VenueFilterType | null

    beforeEach(() => {
      Reflect.deleteProperty(global.window, 'location')
      window.location.href = 'https://www.example.com'

      venue = {
        id: 1436,
        name: 'Librairie de Paris',
        publicName: "Lib de Par's",
      }
    })

    it('should show no tags when no filter and no venue filter are selected', async () => {
      // Given
      venue = null

      // When
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={jest.fn()}
          venueFilter={venue}
        />
      )

      // Then
      expect(
        screen.queryByText('Réinitialiser les filtres')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Lieu :', { exact: false })
      ).not.toBeInTheDocument()
    })

    it('should show venue tag with venue public name when venue filter is applied', async () => {
      // When
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={jest.fn()}
          venueFilter={venue}
        />
      )

      // Then
      expect(
        screen.getByText(`Lieu : ${venue?.publicName}`)
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Réinitialiser les filtres')
      ).toBeInTheDocument()
    })

    it('should show venue tag with venue name when venue filter is applied and public name does not exist', async () => {
      // Given
      venue = venue as VenueFilterType
      venue.publicName = undefined

      // When
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={jest.fn()}
          venueFilter={venue}
        />
      )

      // Then
      expect(screen.getByText(`Lieu : ${venue.name}`)).toBeInTheDocument()
      expect(
        screen.queryByText('Réinitialiser les filtres')
      ).toBeInTheDocument()
    })

    it('should show filter tags when at least one filter is selected', async () => {
      // When
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={jest.fn()}
          venueFilter={venue}
        />
      )

      // Then
      const departmentFilter = screen.getByLabelText('Département', {
        selector: 'input',
      })
      await selectEvent.select(departmentFilter, '01 - Ain')

      expect(
        screen.queryByText('Réinitialiser les filtres')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('01 - Ain', { selector: 'div' }) // use selector div otherwise the option is found
      ).toBeInTheDocument()
    })

    it('should reset filters', async () => {
      const removeVenueFilter = jest.fn()
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={removeVenueFilter}
          venueFilter={venue}
        />
      )

      // When
      const departmentFilter = screen.getByLabelText('Département', {
        selector: 'input',
      })
      await selectEvent.select(departmentFilter, '01 - Ain')
      expect(
        screen.getByText('01 - Ain', { selector: 'div' })
      ).toBeInTheDocument()

      const resetFiltersButton = screen.getByText('Réinitialiser les filtres')
      waitFor(() => fireEvent.click(resetFiltersButton))

      // Then
      expect(removeVenueFilter).toHaveBeenCalledWith()
      expect(
        screen.queryByText('01 - Ain', { selector: 'div' })
      ).not.toBeInTheDocument()
    })

    it('should remove filter when clicking on delete button', async () => {
      const removeVenueFilter = jest.fn()
      render(
        <OfferFilters
          handleSearchButtonClick={jest.fn()}
          isLoading={false}
          query=""
          refine={jest.fn()}
          removeVenueFilter={removeVenueFilter}
          venueFilter={venue}
        />
      )

      // When
      const departmentFilter = screen.getByLabelText('Département', {
        selector: 'input',
      })
      await selectEvent.select(departmentFilter, '01 - Ain')

      const filterTag = screen.getByText('01 - Ain', { selector: 'div' })
      expect(filterTag).toBeInTheDocument()

      const closeIcon = filterTag.lastChild

      waitFor(() => fireEvent.click(closeIcon as ChildNode))

      // Then
      expect(
        screen.queryByText('01 - Ain', { selector: 'div' })
      ).not.toBeInTheDocument()
    })
  })
})

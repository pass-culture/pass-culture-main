import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { VenueFilterType } from '../../../../../utils/types'
import {
  findLaunchSearchButton,
  queryResetFiltersButton,
} from '../../../../__spec__/__test_utils__/elements'
import { OfferFilters } from '../OfferFilters/OfferFilters'

const renderOfferFilters = props => {
  render(<OfferFilters {...props} />)
}

describe('offerFilters component', () => {
  let props
  let venue: VenueFilterType | null = {
    id: 1436,
    name: 'Librairie de Paris',
    publicName: "Lib de Par's",
  }

  beforeEach(() => {
    props = {
      dispatchCurrentFilters: jest.fn(),
      currentFilters: {
        departments: [],
        categories: [],
        students: [],
      },
      handleLaunchSearch: jest.fn(),
      venueFilter: null,
      removeVenueFilter: jest.fn(),
      isLoading: false,
    }
  })

  it('should show no tags when no filter and no venue filter are selected', async () => {
    // When
    renderOfferFilters(props)

    // Then
    const launchSearchButton = await findLaunchSearchButton()
    expect(launchSearchButton).toBeInTheDocument()
    expect(
      screen.queryByText('Réinitialiser les filtres')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Lieu :', { exact: false })
    ).not.toBeInTheDocument()
  })

  it('should show venue tag with venue public name when venue filter is applied', async () => {
    // When
    renderOfferFilters({ ...props, venueFilter: venue })

    // Then
    await waitFor(() =>
      expect(
        screen.queryByText(`Lieu : ${venue?.publicName}`)
      ).toBeInTheDocument()
    )
    expect(screen.queryByText('Réinitialiser les filtres')).toBeInTheDocument()
  })

  it('should show venue tag with venue name when venue filter is applied and public name does not exist', async () => {
    // Given
    venue = venue as VenueFilterType
    venue.publicName = undefined

    // When
    renderOfferFilters({ ...props, venueFilter: venue })

    // Then
    await waitFor(() =>
      expect(screen.queryByText(`Lieu : ${venue?.name}`)).toBeInTheDocument()
    )
    expect(screen.queryByText('Réinitialiser les filtres')).toBeInTheDocument()
  })

  it('should show filter tags when at least one filter is selected', async () => {
    // When
    renderOfferFilters({
      ...props,
      currentFilters: {
        departments: [{ value: '01', label: '01 - Ain' }],
        categories: [],
        students: [],
      },
    })

    // Then
    const resetFiltersButton = await queryResetFiltersButton()
    await waitFor(() => expect(resetFiltersButton).toBeInTheDocument())
  })
})

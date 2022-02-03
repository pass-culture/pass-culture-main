import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import {
  findLaunchSearchButton,
  queryResetFiltersButton,
} from 'app/__spec__/__test_utils__/elements'
import { placeholder } from 'app/__spec__/App.spec'
import SearchAndFiltersComponent from 'app/components/OffersInstantSearch/OffersSearch/OffersSearchBarAndFilters/OffersSearchBarAndFilters'
import { VenueFilterType } from 'utils/types'

const renderSearchAndFiltersComponent = props => {
  render(<SearchAndFiltersComponent {...props} />)
}

describe('searchAndFiltersComponent', () => {
  let props
  let venue: VenueFilterType | null = {
    id: 1436,
    name: 'Librairie de Paris',
    publicName: "Lib de Par's",
  }

  beforeEach(() => {
    props = {
      query: '',
      currentRefinement: '',
      handleSearchButtonClick: jest.fn(),
      isLoading: false,
      isSearchStalled: false,
      refine: jest.fn(),
      setQuery: jest.fn(),
      removeVenueFilter: jest.fn(),
      venueFilter: null,
      currentFilters: { departments: [], categories: [], students: [] },
    }
  })

  it('should have correct placeholder', async () => {
    // Given

    // When
    renderSearchAndFiltersComponent(props)

    // Then
    await waitFor(() =>
      expect(screen.getByPlaceholderText(placeholder)).toBeInTheDocument()
    )
  })

  it('should show no tags when no filter and no venue filter are selected', async () => {
    // When
    renderSearchAndFiltersComponent({ ...props, venueFilter: null })

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
    renderSearchAndFiltersComponent({ ...props, venueFilter: venue })

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
    renderSearchAndFiltersComponent({ ...props, venueFilter: venue })

    // Then
    await waitFor(() =>
      expect(screen.queryByText(`Lieu : ${venue?.name}`)).toBeInTheDocument()
    )
    expect(screen.queryByText('Réinitialiser les filtres')).toBeInTheDocument()
  })

  it('should show filter tags when at least one filter is selected', async () => {
    // When
    renderSearchAndFiltersComponent({
      ...props,
      currentFilters: {
        departments: ['venue.departmentCode:01'],
        categories: [],
        students: [],
      },
    })

    // Then
    const resetFiltersButton = await queryResetFiltersButton()
    await waitFor(() => expect(resetFiltersButton).toBeInTheDocument())
  })
})

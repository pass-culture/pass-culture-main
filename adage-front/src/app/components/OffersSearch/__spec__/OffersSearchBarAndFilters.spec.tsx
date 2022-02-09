import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { findLaunchSearchButton } from '../../../__spec__/__test_utils__/elements'
import { SearchAndFiltersComponent } from '../OffersSearchBarAndFilters/OffersSearchBarAndFilters'

const placeholder = 'Nom de l’offre ou du partenaire culturel'

const renderSearchAndFiltersComponent = props => {
  render(<SearchAndFiltersComponent {...props} />)
}

describe('searchAndFiltersComponent', () => {
  let props

  beforeEach(() => {
    props = {
      currentRefinement: '',
      handleSearchButtonClick: jest.fn(),
      isLoading: false,
      isSearchStalled: false,
      refine: jest.fn(),
      removeVenueFilter: jest.fn(),
      venueFilter: null,
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

  it('should call refine on text change', async () => {
    // Given
    renderSearchAndFiltersComponent(props)
    const launchSearchButton = await findLaunchSearchButton()

    // When
    const textInput = screen.getByPlaceholderText(placeholder)
    userEvent.type(textInput, 'a')
    launchSearchButton.click()

    // Then
    expect(props.refine).toHaveBeenNthCalledWith(1, 'a')
  })
})

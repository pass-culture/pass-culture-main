import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { findLaunchSearchButton } from 'app/__spec__/__test_utils__/elements'
import { placeholder } from 'app/__spec__/App.spec'
import { INITIAL_FACET_FILTERS } from 'app/constants'
import { Role } from 'utils/types'

import { OffersSearch } from '../OffersSearch'

const renderOffersSearchComponent = props => {
  render(<OffersSearch {...props} />)
}

describe('offersSearch component', () => {
  let props

  beforeEach(() => {
    props = {
      userRole: Role.redactor,
      removeVenueFilter: jest.fn(),
      venueFilter: null,
      setFacetFilters: jest.fn(),
      facetFilters: [...INITIAL_FACET_FILTERS],
      refine: jest.fn(),
    }
  })

  it('should call algolia with requested query', async () => {
    // Given
    renderOffersSearchComponent(props)
    const launchSearchButton = await findLaunchSearchButton()

    // When
    const textInput = screen.getByPlaceholderText(placeholder)
    userEvent.type(textInput, 'a')
    launchSearchButton.click()

    // Then
    expect(props.refine).toHaveBeenCalledWith('a')
  })
})

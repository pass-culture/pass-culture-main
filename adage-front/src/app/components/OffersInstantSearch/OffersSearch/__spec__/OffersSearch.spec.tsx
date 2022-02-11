import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { findLaunchSearchButton } from 'app/__spec__/__test_utils__/elements'
import { INITIAL_FACET_FILTERS } from 'app/constants'
import { Role } from 'utils/types'

import { OffersSearchComponent } from '../OffersSearch'
import { placeholder } from '../SearchBox'

jest.mock('../Offers/Offers', () => {
  return {
    Offers: jest.fn(() => <div />),
  }
})

jest.mock('../Offers/Pagination/Pagination', () => {
  return {
    Pagination: jest.fn(() => <div />),
  }
})

const renderOffersSearchComponent = props => {
  render(<OffersSearchComponent {...props} />)
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
    userEvent.type(textInput, 'Paris')
    launchSearchButton.click()

    // Then
    expect(props.refine).toHaveBeenCalledWith('Paris')
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { findLaunchSearchButton } from 'app/__spec__/__test_utils__/elements'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'app/providers'
import { Role } from 'utils/types'

import { OffersSearchComponent, SearchProps } from '../OffersSearch'
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

const renderOffersSearchComponent = (props: SearchProps) => {
  render(
    <FiltersContextProvider>
      <AlgoliaQueryContextProvider>
        <OffersSearchComponent {...props} />
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>
  )
}

describe('offersSearch component', () => {
  let props: SearchProps

  beforeEach(() => {
    props = {
      userRole: Role.redactor,
      removeVenueFilter: jest.fn(),
      venueFilter: null,
      refine: jest.fn(),
      currentRefinement: '',
      isSearchStalled: false,
      useNewAlgoliaIndex: false,
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

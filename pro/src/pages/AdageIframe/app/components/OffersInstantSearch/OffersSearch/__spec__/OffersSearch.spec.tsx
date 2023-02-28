import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { findLaunchSearchButton } from 'pages/AdageIframe/app/__spec__/__test_utils__/elements'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'

import { OffersSearchComponent, SearchProps } from '../OffersSearch'
import { placeholder } from '../SearchBox'

jest.mock('../Offers/Offers', () => {
  return {
    Offers: jest.fn(() => <div />),
  }
})

jest.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: jest.fn(),
  },
}))

jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn(),
}))

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
      user: {
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
        departmentCode: '30',
        institutionName: 'COLLEGE BELLEVUE',
        institutionCity: 'ALES',
      },
      removeVenueFilter: jest.fn(),
      venueFilter: null,
      refine: jest.fn(),
      currentRefinement: '',
      isSearchStalled: false,
    }
  })

  it('should call algolia with requested query', async () => {
    // Given
    renderOffersSearchComponent(props)
    const launchSearchButton = await findLaunchSearchButton()

    // When
    const textInput = screen.getByPlaceholderText(placeholder)
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(props.refine).toHaveBeenCalledWith('Paris')
  })

  describe('filter only in my school', () => {
    it('should display checkbox label with user information', async () => {
      renderOffersSearchComponent(props)

      await waitFor(() =>
        expect(
          screen.getByLabelText(
            'Les acteurs qui se déplacent dans mon établissement : COLLEGE BELLEVUE - ALES (30)'
          )
        ).toBeInTheDocument()
      )
    })

    it('should not display checkbox', async () => {
      props.user = {
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
        departmentCode: null,
        institutionName: null,
        institutionCity: null,
      }
      renderOffersSearchComponent(props)

      expect(
        screen.queryByLabelText(
          'Les acteurs qui se déplacent dans mon établissement'
        )
      ).not.toBeInTheDocument()
    })

    it('should check user department when checking checkbox', async () => {
      renderOffersSearchComponent(props)
      const checkbox = screen.getByLabelText(
        'Les acteurs qui se déplacent dans mon établissement',
        { exact: false }
      )

      userEvent.click(checkbox)

      expect(
        await screen.findByText('30 - Gard', { selector: 'div' })
      ).toBeInTheDocument()
    })

    it('should uncheck checkbox when user remove department tag', async () => {
      renderOffersSearchComponent(props)
      const checkbox = screen.getByLabelText(
        'Les acteurs qui se déplacent dans mon établissement',
        { exact: false }
      )
      await userEvent.click(checkbox)

      const gardFilterTag = screen.getByText('30 - Gard', { selector: 'div' })
      const closeIcon = gardFilterTag.lastChild

      userEvent.click(closeIcon as Element)

      await waitFor(() =>
        expect(
          screen.getByLabelText(
            'Les acteurs qui se déplacent dans mon établissement',
            { exact: false }
          )
        ).not.toBeChecked()
      )
    })

    it('should uncheck checkbox when user deselect his department', async () => {
      renderOffersSearchComponent(props)
      const checkbox = screen.getByLabelText(
        'Les acteurs qui se déplacent dans mon établissement',
        { exact: false }
      )
      await userEvent.click(checkbox)

      const departmentFilter = await screen.findByLabelText('Département')
      await userEvent.click(departmentFilter)
      await userEvent.click(screen.getAllByText('30 - Gard')[0])

      await waitFor(() =>
        expect(
          screen.getByLabelText(
            'Les acteurs qui se déplacent dans mon établissement',
            { exact: false }
          )
        ).not.toBeChecked()
      )
    })

    it('should uncheck checkbox when user adds a department', async () => {
      renderOffersSearchComponent(props)
      const checkbox = screen.getByLabelText(
        'Les acteurs qui se déplacent dans mon établissement',
        { exact: false }
      )
      userEvent.click(checkbox)

      const departmentFilter = await screen.findByLabelText('Département')
      await userEvent.click(departmentFilter)
      await userEvent.click(screen.getByText('75 - Paris'))

      await waitFor(() =>
        expect(
          screen.getByLabelText(
            'Les acteurs qui se déplacent dans mon établissement',
            { exact: false }
          )
        ).not.toBeChecked()
      )
    })

    it('should deselect all department except user department when user checks the checkbox', async () => {
      renderOffersSearchComponent(props)
      const departmentFilter = screen.getByLabelText('Département')

      await userEvent.click(departmentFilter)
      await userEvent.click(screen.getByText('75 - Paris'))

      const checkbox = screen.getByLabelText(
        'Les acteurs qui se déplacent dans mon établissement',
        { exact: false }
      )

      await userEvent.click(checkbox)

      const parisFilterTag = screen.queryByText('75 - Paris', {
        selector: 'div',
      })
      const gardFilterTag = screen.queryByText('30 - Gard', { selector: 'div' })

      expect(parisFilterTag).not.toBeInTheDocument()
      expect(gardFilterTag).toBeInTheDocument()
    })
  })
})

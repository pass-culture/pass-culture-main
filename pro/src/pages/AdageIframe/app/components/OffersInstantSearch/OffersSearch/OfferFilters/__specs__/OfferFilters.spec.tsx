import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferFilters, OfferFiltersProps } from '../OfferFilters'

const renderOfferFilters = (props: OfferFiltersProps) =>
  renderWithProviders(<OfferFilters {...props} />)

describe('OfferFilters', () => {
  it('should call refine function when form is submitted', async () => {
    const mockRefine = jest.fn()
    renderOfferFilters({ isLoading: false, refine: mockRefine })

    const queryInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    const searchButton = screen.getByRole('button', { name: 'Rechercher' })

    await userEvent.type(queryInput, 'example query')
    await userEvent.click(searchButton)

    expect(mockRefine).toHaveBeenCalledWith('example query')
  })
})

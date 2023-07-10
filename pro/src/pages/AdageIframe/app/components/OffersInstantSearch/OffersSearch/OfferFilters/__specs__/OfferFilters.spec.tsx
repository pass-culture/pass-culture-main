import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import * as pcapi from 'pages/AdageIframe/repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferFilters, OfferFiltersProps } from '../OfferFilters'

const renderOfferFilters = (props: OfferFiltersProps) =>
  renderWithProviders(<OfferFilters {...props} />)

describe('OfferFilters', () => {
  const mockRefine = jest.fn()
  it('should call refine function when form is submitted', async () => {
    renderOfferFilters({ isLoading: false, refine: mockRefine, uai: ['all'] })

    const queryInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    const searchButton = screen.getByRole('button', { name: 'Rechercher' })

    await userEvent.type(queryInput, 'example query')
    await userEvent.click(searchButton)

    expect(mockRefine).toHaveBeenCalledWith('example query')
  })

  it('should clean filter value onclick', async () => {
    jest.spyOn(pcapi, 'getEducationalDomains').mockResolvedValueOnce([
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
      { id: 3, name: 'Arts' },
    ])

    renderOfferFilters({ isLoading: false, refine: mockRefine, uai: ['all'] })

    const artisticDomainButton = screen.getByRole('button', {
      name: 'Domaine artistique',
    })
    await userEvent.click(artisticDomainButton)

    const checkboxValue = screen.getByLabelText('Architecture', {
      exact: false,
    })

    await userEvent.click(checkboxValue)

    expect(checkboxValue).toBeChecked()

    const cleanButton = screen.getByRole('button', {
      name: 'Effacer',
    })

    await userEvent.click(cleanButton)

    expect(checkboxValue).not.toBeChecked()
  })

  it('should call submit onclick search button with uai value all', async () => {
    renderOfferFilters({ isLoading: false, refine: mockRefine, uai: ['all'] })

    const artisticDomainButton = screen.getByRole('button', {
      name: 'Domaine artistique',
    })
    await userEvent.click(artisticDomainButton)

    const submitButton = screen.getAllByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.click(submitButton[1])
  })

  it('should call submit onclick search button with uai value ', async () => {
    renderOfferFilters({
      isLoading: false,
      refine: mockRefine,
      uai: ['all', 'uai'],
    })

    const artisticDomainButton = screen.getByRole('button', {
      name: 'Domaine artistique',
    })
    await userEvent.click(artisticDomainButton)

    const submitButton = screen.getAllByRole('button', {
      name: 'Rechercher',
    })

    await userEvent.click(submitButton[1])
  })
})

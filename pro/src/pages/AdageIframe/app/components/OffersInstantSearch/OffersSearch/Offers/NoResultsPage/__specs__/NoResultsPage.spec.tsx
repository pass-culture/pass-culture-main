import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  FacetFiltersContext,
  FacetFiltersContextType,
} from 'pages/AdageIframe/app/providers'
import { renderWithProviders } from 'utils/renderWithProviders'

import { NoResultsPage } from '../NoResultsPage'

const resetFormMock = vi.fn()
const setFacetFiltersMock = vi.fn()

const renderNoResultsPage = ({
  facetFiltersContextValue,
  resetForm,
}: {
  facetFiltersContextValue: FacetFiltersContextType
  resetForm?: () => void
}) => {
  return renderWithProviders(
    <FacetFiltersContext.Provider value={facetFiltersContextValue}>
      <NoResultsPage resetForm={resetForm} />
    </FacetFiltersContext.Provider>
  )
}

describe('ContactButton', () => {
  it('should clear all filters on click button ', async () => {
    renderNoResultsPage({
      facetFiltersContextValue: {
        facetFilters: ['1', '2'],
        setFacetFilters: setFacetFiltersMock,
      },
      resetForm: resetFormMock,
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    await userEvent.click(clearFilterButton)

    expect(resetFormMock).toHaveBeenCalled()
  })

  it('should not display clear all filters button ', async () => {
    renderNoResultsPage({
      facetFiltersContextValue: {
        facetFilters: ['1'],
        setFacetFilters: setFacetFiltersMock,
      },
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.queryByRole('button', {
      name: 'Réinitiliaser les filtres',
    })

    expect(clearFilterButton).not.toBeInTheDocument()
  })
})

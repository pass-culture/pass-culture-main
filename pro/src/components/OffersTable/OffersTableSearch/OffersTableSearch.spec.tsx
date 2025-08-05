import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersTableSearch, OffersTableSearchProps } from './OffersTableSearch'

const LABELS = {
  nameInput: /Nom/,
  resetButton: /Réinitialiser/,
  searchButton: /Rechercher/,
  filterToggleButton: /Filtrer/,
}

const renderOffersTableSearch = (
  props: Partial<OffersTableSearchProps> = {}
) => {
  return renderWithProviders(
    <OffersTableSearch
      type={props.type || 'individual'}
      onSubmit={props.onSubmit || vi.fn()}
      isDisabled={false}
      nameInputProps={{
        label: 'Nom',
        disabled: false,
        onChange: vi.fn(),
        value: '',
        ...props.nameInputProps,
      }}
      hasActiveFilters={true}
      onResetFilters={props.onResetFilters || vi.fn()}
    >
      {props.children}
    </OffersTableSearch>
  )
}

describe('OffersTableSearch', () => {
  afterEach(() => {
    window.sessionStorage.clear()
  })

  it('should always display a text input and a search button', async () => {
    const nameInputLabel = 'Nom de l’offre ou EAN-13'
    const mockedOnChange = vi.fn()
    renderOffersTableSearch({
      nameInputProps: {
        label: nameInputLabel,
        disabled: false,
        onChange: mockedOnChange,
        value: '',
      },
    })

    const nameInput = screen.getByRole('searchbox', { name: nameInputLabel })
    const searchButton = screen.getByRole('button', {
      name: LABELS.searchButton,
    })

    expect(nameInput).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()

    const newText = 'New text'
    await userEvent.type(nameInput, newText)
    expect(mockedOnChange).toHaveBeenCalledTimes(newText.length)
  })

  it('should always display a reset button', async () => {
    const mockedOnResetFilters = vi.fn()
    renderOffersTableSearch({
      onResetFilters: mockedOnResetFilters,
    })

    const resetButton = screen.getByRole('button', { name: LABELS.resetButton })
    expect(resetButton).toBeInTheDocument()

    await userEvent.click(resetButton)
    expect(mockedOnResetFilters).toHaveBeenCalledTimes(1)
  })

  it('should display a filter toggle button', () => {
    renderOffersTableSearch()

    const filterToggleButton = screen.getByRole('button', {
      name: LABELS.filterToggleButton,
    })
    expect(filterToggleButton).toBeInTheDocument()
  })

  it('should hide filters passed as children and the reset button by default', () => {
    renderOffersTableSearch()

    // Filters are hidden by default.
    // There is a better way to do this, but .isVisible() does not seem to work.
    const filtersWrapper = screen.getByTestId('offers-filter')
    expect(filtersWrapper).toBeInTheDocument()
    expect(filtersWrapper).toHaveClass('offers-table-search-filters-collapsed')
  })

  it('should display filters passed as children and make reset button visible when toggled', async () => {
    renderOffersTableSearch()

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.filterToggleButton })
    )

    // Filters are now made visible.
    // There is a better way to do this, but .isVisible() does not seem to work.
    const filtersWrapper = screen.getByTestId('offers-filter')
    expect(filtersWrapper).not.toHaveClass(
      'offers-table-search-filters-collapsed'
    )
  })
})

import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { OffersTableSearch, OffersTableSearchProps } from './OffersTableSearch'

type OffersTableSearchTestProps = Partial<OffersTableSearchProps>

const LABELS = {
  nameInput: /Nom/,
  resetButton: /Réinitialiser/,
  searchButton: /Rechercher/,
  filterToggleButton: /Filtres/,
}

const renderOffersTableSearch = (props: OffersTableSearchTestProps = {}) => {
  return render(
    <OffersTableSearch
      filtersVisibility={props.filtersVisibility || false}
      onFiltersToggle={props.onFiltersToggle || vi.fn()}
      onSubmit={props.onSubmit || vi.fn()}
      isDisabled={false}
      nameInputProps={{
        label: 'Nom',
        disabled: false,
        onChange: vi.fn(),
        value: '',
        ...props.nameInputProps,
      }}
      resetButtonProps={{
        onClick: vi.fn(),
        isDisabled: false,
        ...props.resetButtonProps,
      }}
    >
      {props.children}
    </OffersTableSearch>
  )
}

describe('OffersTableSearch', () => {
  it('should display a text input and a search button', async () => {
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

    const nameInput = screen.getByRole('textbox', { name: nameInputLabel })
    const searchButton = screen.getByRole('button', { name: LABELS.searchButton })

    expect(nameInput).toBeInTheDocument()
    expect(searchButton).toBeInTheDocument()

    const newText = 'New text'
    await userEvent.type(nameInput, newText)
    expect(mockedOnChange).toHaveBeenCalledTimes(newText.length)
  })

  it('should hide filters passed as children and the reset button by default', () => {
    const childrenTestId = 'filters'
    renderOffersTableSearch({
      filtersVisibility: false,
      children: <div data-testid={childrenTestId}>Filters</div>,
    })

    // Filters and reset button are always rendered.
    const filters = screen.getByTestId(childrenTestId)
    const resetButton = screen.getByRole('button', { name: LABELS.resetButton })
    expect(filters).toBeInTheDocument()
    expect(resetButton).toBeInTheDocument()

    // However, they are hidden by default.
    // There is a better way to do this, but .isVisible() does not seem to work.
    const filtersWrapper= screen.getByTestId('offers-filter')
    expect(filtersWrapper).toBeInTheDocument()
    expect(filtersWrapper).toHaveClass('offers-table-search-filters-collapsed')
  })

  it('should make filters passed as children and reset button visible when expected', () => {
    const childrenTestId = 'filters'
    renderOffersTableSearch({
      filtersVisibility: true,
      children: <div data-testid={childrenTestId}>Filters</div>,
    })

    // Filters and reset button are always rendered.
    const filters = screen.getByTestId(childrenTestId)
    const resetButton = screen.getByRole('button', { name: LABELS.resetButton })
    expect(filters).toBeInTheDocument()
    expect(resetButton).toBeInTheDocument()

    // They are visible.
    // There is a better way to do this, but .isVisible() does not seem to work.
    const filtersWrapper = screen.getByTestId('offers-filter')
    expect(filtersWrapper).not.toHaveClass('offers-table-search-filters-collapsed')
  })

  it('should call onFiltersToggle when clicking the filter toggle button', async () => {
    const mockedOnFiltersToggle = vi.fn()
    renderOffersTableSearch({
      onFiltersToggle: mockedOnFiltersToggle,
    })

    const filterToggleButton = screen.getByRole('button', { name: LABELS.filterToggleButton })
    await userEvent.click(filterToggleButton)

    expect(mockedOnFiltersToggle).toHaveBeenCalledTimes(1)
  })
})
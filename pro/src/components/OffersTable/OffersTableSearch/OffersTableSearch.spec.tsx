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

  it('should hide the filters and the reset button by default', () => {
    renderOffersTableSearch()

    const filtersWrapper= screen.getByTestId('offers-filter')
    expect(filtersWrapper).toBeInTheDocument()
    // There is a better way to do this, but .isVisible() does not seem to work.
    expect(filtersWrapper).toHaveClass('offers-table-search-filters-collapsed')
  })

  it('should display the filters and the reset button when the toggle button is clicked', async () => {
    const mockedOnReset = vi.fn()
    renderOffersTableSearch({
      children: <div data-testid="filters">Filters</div>,
      resetButtonProps: {
        onClick: mockedOnReset,
        isDisabled: false,
      },
    })

    const toggleButton = screen.getByRole('button', { name: LABELS.filterToggleButton })
    await userEvent.click(toggleButton)

    const filtersWrapper = screen.getByTestId('offers-filter')
    expect(filtersWrapper).not.toHaveClass('offers-table-search-filters-collapsed')

    const filters = screen.getByTestId('filters')
    const resetButton = screen.getByRole('button', { name: LABELS.resetButton })

    expect(filters).toBeInTheDocument()
    expect(resetButton).toBeInTheDocument()

    await userEvent.click(resetButton)
    expect(mockedOnReset).toHaveBeenCalledTimes(1)
  })
})
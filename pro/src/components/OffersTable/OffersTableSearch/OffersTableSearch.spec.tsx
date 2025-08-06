import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersTableSearch, OffersTableSearchProps } from './OffersTableSearch'

type OffersTableSearchTestProps = Partial<OffersTableSearchProps>

const LABELS = {
  nameInput: /Nom/,
  resetButton: /Réinitialiser/,
  searchButton: /Rechercher/,
  filterToggleButton: /Filtrer/,
}

type OffersTableSearchTableTestProps = OffersTableSearchTestProps & {
  isCollapsedMemorizedFiltersEnabled?: boolean
}
const renderOffersTableSearch = (
  props: OffersTableSearchTableTestProps = {}
) => {
  const features = []
  if (props.isCollapsedMemorizedFiltersEnabled) {
    features.push('WIP_COLLAPSED_MEMORIZED_FILTERS')
  }

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
    </OffersTableSearch>,
    { features }
  )
}

describe('OffersTableSearch', () => {
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

  it('should always render filters passed as children and visible', () => {
    const childrenTestId = 'filters'
    renderOffersTableSearch({
      children: <div data-testid={childrenTestId}>Filters</div>,
    })

    // Filters and reset button are always rendered.
    const filters = screen.getByTestId(childrenTestId)
    expect(filters).toBeInTheDocument()

    // They are always visible without toggling.
    // There is a better way to do this, but .isVisible() does not seem to work.
    const filtersWrapper = screen.getByTestId('offers-filter')
    expect(filtersWrapper).not.toHaveClass(
      'offers-table-search-filters-collapsed'
    )
  })

  describe('when filters toggling and storing is enabled', () => {
    afterEach(() => {
      window.sessionStorage.clear()
    })

    it('should display a filter toggle button', () => {
      renderOffersTableSearch({ isCollapsedMemorizedFiltersEnabled: true })

      const filterToggleButton = screen.getByRole('button', {
        name: LABELS.filterToggleButton,
      })
      expect(filterToggleButton).toBeInTheDocument()
    })

    it('should hide filters passed as children and the reset button by default', () => {
      renderOffersTableSearch({ isCollapsedMemorizedFiltersEnabled: true })

      // Filters are hidden by default.
      // There is a better way to do this, but .isVisible() does not seem to work.
      const filtersWrapper = screen.getByTestId('offers-filter')
      expect(filtersWrapper).toBeInTheDocument()
      expect(filtersWrapper).toHaveClass(
        'offers-table-search-filters-collapsed'
      )
    })

    it('should display filters passed as children and make reset button visible when toggled', async () => {
      renderOffersTableSearch({ isCollapsedMemorizedFiltersEnabled: true })

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
})

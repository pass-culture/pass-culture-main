import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { Option } from '../MultiSelect'
import { MultiSelectPanel } from '../MultiSelectPanel'

describe('<MultiSelectPanel />', () => {
  const options: (Option & { checked: boolean })[] = [
    { id: '1', label: 'Option 1', checked: false },
    { id: '2', label: 'Option 2', checked: false },
    { id: '3', label: 'Option 3', checked: false },
  ]

  const onOptionSelect = vi.fn()
  const onSelectAll = vi.fn()

  const renderMultiSelectPanel = ({
    hasSelectAllOptions = false,
    isAllChecked = false,
    hasSearch = false,
    searchLabel = '',
    searchExample = '',
  }: {
    hasSelectAllOptions?: boolean
    isAllChecked?: boolean
    hasSearch?: boolean
    searchLabel?: string
    searchExample?: string
  } = {}) => {
    return render(
      <MultiSelectPanel
        id="1"
        options={options}
        label={''}
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={hasSelectAllOptions}
        isAllChecked={isAllChecked}
        hasSearch={hasSearch}
        searchLabel={searchLabel}
        searchExample={searchExample}
      />
    )
  }

  it('renders options with checkboxes', () => {
    renderMultiSelectPanel()

    expect(screen.getByLabelText('Option 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 2')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 3')).toBeInTheDocument()
  })

  it('renders the search input if hasSearch is true', () => {
    renderMultiSelectPanel({
      hasSearch: true,
      searchExample: 'Exemple: Nantes',
      searchLabel: 'Search label',
    })

    expect(screen.getByText(/Exemple: Nantes/i)).toBeInTheDocument()
  })

  it('updates search value on input change', async () => {
    renderMultiSelectPanel({
      hasSearch: true,
      searchExample: 'Exemple: Nantes',
      searchLabel: 'Search label',
    })

    const input = screen.getByRole('searchbox')

    await userEvent.type(input, 'apple')

    expect(input).toHaveValue('apple')
  })

  it('displays the search example text', () => {
    renderMultiSelectPanel({
      hasSearch: true,
      searchExample: 'Exemple: Nantes',
      searchLabel: 'Search label',
    })

    expect(screen.getByText('Exemple: Nantes')).toBeInTheDocument()
  })

  it('not renders the search input if hasSearch is false', () => {
    renderMultiSelectPanel()

    expect(screen.queryByText(/Exemple: Nantes/i)).not.toBeInTheDocument()
  })

  it('should filter options based on the search input', async () => {
    renderMultiSelectPanel({
      hasSearch: true,
      searchExample: 'Exemple: Nantes',
      searchLabel: 'Search label',
    })

    expect(screen.getByText('Option 1')).toBeInTheDocument()
    expect(screen.getByText('Option 2')).toBeInTheDocument()
    expect(screen.getByText('Option 3')).toBeInTheDocument()

    const searchInput = screen.getByRole('searchbox')

    await userEvent.type(searchInput, 'Option 1')

    await waitFor(() => {
      expect(screen.queryByText('Option 2')).not.toBeInTheDocument()
      expect(screen.queryByText('Option 3')).not.toBeInTheDocument()
      expect(screen.getByText('Option 1')).toBeInTheDocument()
    })

    await userEvent.clear(searchInput)

    await waitFor(() => {
      expect(screen.getByText('Option 1')).toBeInTheDocument()
      expect(screen.getByText('Option 2')).toBeInTheDocument()
      expect(screen.getByText('Option 3')).toBeInTheDocument()
    })
  })

  it('should show "No results found" when no options match the search', async () => {
    renderMultiSelectPanel({
      hasSearch: true,
      searchExample: 'Exemple: Nantes',
      searchLabel: 'Search label',
    })

    const searchInput = screen.getByRole('searchbox')

    await userEvent.type(searchInput, 'Non-matching option')

    await waitFor(() =>
      expect(
        screen.getByText('Aucun résultat trouvé pour votre recherche.')
      ).toBeInTheDocument()
    )
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderMultiSelectPanel()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('selects and deselects individual options', async () => {
    renderMultiSelectPanel()

    const option2Checkbox = screen.getByRole('checkbox', { name: 'Option 2' })

    await userEvent.click(option2Checkbox)

    expect(onOptionSelect).toHaveBeenCalledWith(options[1])

    await userEvent.click(option2Checkbox)

    expect(onOptionSelect).toHaveBeenCalledWith(options[1])
  })

  it('renders "Select All" checkbox when hasSelectAllOptions is true', () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
    })

    expect(
      screen.getByRole('checkbox', {
        name: 'Tout sélectionner',
      })
    ).toBeInTheDocument()
  })

  it('triggers onSelectAll when "Select All" checkbox is clicked', async () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
    })

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    await userEvent.click(selectAllCheckbox)

    expect(onSelectAll).toHaveBeenCalledTimes(1)
  })

  it('reflects isAllChecked state in "Select All" checkbox', () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
      isAllChecked: true,
    })

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    expect(selectAllCheckbox).toBeChecked()
  })

  it('does not render "Select All" checkbox when hasSelectAllOptions is false', () => {
    renderMultiSelectPanel()

    const selectAllCheckbox = screen.queryByText('Tout sélectionner')

    expect(selectAllCheckbox).not.toBeInTheDocument()
  })

  it('calls onOptionSelect when Enter key is pressed on an option', async () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
    })

    const optionCheckbox = screen.getByRole('checkbox', { name: 'Option 1' })

    optionCheckbox.focus()

    await userEvent.keyboard('[Space]')

    expect(onOptionSelect).toHaveBeenCalledWith({
      id: '1',
      label: 'Option 1',
      checked: false,
    })
  })

  it('calls onOptionSelect when Space key is pressed on an option', async () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
    })

    const optionCheckbox = screen.getByRole('checkbox', { name: 'Option 2' })

    optionCheckbox.focus()

    await userEvent.keyboard('[Space]')

    expect(onOptionSelect).toHaveBeenCalledWith({
      id: '2',
      label: 'Option 2',
      checked: false,
    })
  })

  it('does not call onOptionSelect when other keys are pressed', async () => {
    renderMultiSelectPanel({
      hasSelectAllOptions: true,
    })

    const optionCheckbox = screen.getByRole('checkbox', { name: 'Option 3' })

    optionCheckbox.focus()

    await userEvent.keyboard('[ArrowDown]')

    expect(onOptionSelect).not.toHaveBeenCalled()
  })
})

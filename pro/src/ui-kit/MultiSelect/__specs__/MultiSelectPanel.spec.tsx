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

  it('renders options with checkboxes', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label={''}
        hasSearch={false}
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    expect(screen.getByLabelText('Option 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 2')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 3')).toBeInTheDocument()
  })

  it('renders the search input if hasSearch is true', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={[]}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={true}
        searchExample="Exemple: Nantes"
        searchLabel="Search label"
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    expect(screen.getByText(/Exemple: Nantes/i)).toBeInTheDocument()
  })

  test('updates search value on input change', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={[]}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={true}
        searchExample="Exemple: Nantes"
        searchLabel="Search label"
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    const input = screen.getByRole('searchbox')

    await userEvent.type(input, 'apple')

    expect(input).toHaveValue('apple')
  })

  test('displays the search example text', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={[]}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={true}
        searchExample="Exemple: Nantes"
        searchLabel="Search label"
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    expect(screen.getByText('Exemple: Nantes')).toBeInTheDocument()
  })

  it('not renders the search input if hasSearch is false', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={[]}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={false}
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    expect(screen.queryByText(/Exemple: Nantes/i)).not.toBeInTheDocument()
  })

  it('should filter options based on the search input', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={true}
        searchExample="Exemple: Nantes"
        searchLabel="Search label"
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

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
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label={''}
        onOptionSelect={onOptionSelect}
        hasSearch={true}
        searchExample="Exemple: Nantes"
        searchLabel="Search label"
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    const searchInput = screen.getByRole('searchbox')

    await userEvent.type(searchInput, 'Non-matching option')

    await waitFor(() =>
      expect(
        screen.getByText('Aucun résultat trouvé pour votre recherche.')
      ).toBeInTheDocument()
    )
  })

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <MultiSelectPanel
        id="1"
        options={[]}
        label=""
        onOptionSelect={onOptionSelect}
        hasSearch={false}
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('selects and deselects individual options', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        hasSearch={false}
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        isAllChecked={false}
      />
    )

    const option2Checkbox = screen.getByLabelText(/Option 2/i)
    await userEvent.click(option2Checkbox)
    expect(onOptionSelect).toHaveBeenCalledWith(options[1])

    await userEvent.click(option2Checkbox)
    expect(onOptionSelect).toHaveBeenCalledWith(options[1])
  })

  test('renders "Select All" checkbox when hasSelectAllOptions is true', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    expect(screen.getByLabelText('Tout sélectionner')).toBeInTheDocument()
  })

  test('triggers onSelectAll when "Select All" checkbox is clicked', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    const selectAllCheckbox = screen.getByLabelText('Tout sélectionner')
    await userEvent.click(selectAllCheckbox)

    expect(onSelectAll).toHaveBeenCalledTimes(1)
  })

  test('reflects isAllChecked state in "Select All" checkbox', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={true}
        hasSearch={false}
      />
    )

    const selectAllCheckbox = screen.getByLabelText('Tout sélectionner')
    expect(selectAllCheckbox).toBeChecked()
  })

  test('does not render "Select All" checkbox when hasSelectAllOptions is false', () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={false}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    const selectAllCheckbox = screen.queryByLabelText('Tout sélectionner')
    expect(selectAllCheckbox).not.toBeInTheDocument()
  })

  test('calls onOptionSelect when Enter key is pressed on an option', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    const optionCheckbox = screen.getByLabelText('Option 1')

    optionCheckbox.focus()

    await userEvent.keyboard('[Space]')

    expect(onOptionSelect).toHaveBeenCalledWith({
      id: '1',
      label: 'Option 1',
      checked: false,
    })
  })

  test('calls onOptionSelect when Space key is pressed on an option', async () => {
    render(
      <MultiSelectPanel
        id="1"
        label=""
        options={options}
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    const optionCheckbox = screen.getByLabelText('Option 2')

    optionCheckbox.focus()

    await userEvent.keyboard('[Space]')

    expect(onOptionSelect).toHaveBeenCalledWith({
      id: '2',
      label: 'Option 2',
      checked: false,
    })
  })

  test('does not call onOptionSelect when other keys are pressed', async () => {
    render(
      <MultiSelectPanel
        id="1"
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
        onSelectAll={onSelectAll}
        hasSelectAllOptions={true}
        isAllChecked={false}
        hasSearch={false}
      />
    )

    const optionCheckbox = screen.getByLabelText('Option 3')

    optionCheckbox.focus()

    await userEvent.keyboard('[ArrowDown]')

    expect(onOptionSelect).not.toHaveBeenCalled()
  })
})

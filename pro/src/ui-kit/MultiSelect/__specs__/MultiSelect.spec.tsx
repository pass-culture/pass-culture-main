import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { MultiSelect, Option } from '../MultiSelect'

describe('<MultiSelect />', () => {
  const options: Option[] = [
    { id: '1', label: 'Option 1' },
    { id: '2', label: 'Option 2' },
    { id: '3', label: 'Option 3' },
  ]

  const defaultOptions: Option[] = [{ id: '1', label: 'Option 1' }]

  it('should render correctly', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        defaultOptions={defaultOptions}
        hasSearch={false}
      />
    )

    expect(await screen.findByText('Select Options')).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        defaultOptions={defaultOptions}
        hasSearch={false}
      />
    )

    expect(await axe(container)).toHaveNoViolations()

    const toggleButton = screen.getByText('Select Options')
    await userEvent.click(toggleButton)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the MultiSelect component with the correct initial selected options', () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        defaultOptions={defaultOptions}
        hasSearch={false}
      />
    )

    expect(screen.getByText('Option 1')).toBeInTheDocument()
  })

  it('toggles the dropdown when the trigger is clicked', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSelectAllOptions={true}
        hasSearch={false}
      />
    )
    const toggleButton = screen.getByText('Select Options')
    await userEvent.click(toggleButton)
    expect(screen.getByText(/Tout sélectionner/i)).toBeInTheDocument()

    await userEvent.click(toggleButton)
    expect(screen.queryByText(/Tout sélectionner/i)).not.toBeInTheDocument()
  })

  it('selects all options when "Select All" is clicked', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSelectAllOptions={true}
        hasSearch={false}
      />
    )

    const toggleButton = screen.getByText('Select Options')
    await userEvent.click(toggleButton)

    const selectAllCheckbox = screen.getByLabelText(/Tout sélectionner/i)
    await userEvent.click(selectAllCheckbox)

    options.forEach((option) => {
      expect(screen.getByLabelText(option.label)).toBeChecked()
    })
  })

  it('removes an option from the selected items when clicked in SelectedValuesTags', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        defaultOptions={defaultOptions}
        hasSearch={false}
      />
    )

    const selectedTag = screen.getByText('Option 1')
    await userEvent.click(selectedTag)
    expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
  })

  it('closes the dropdown when clicked outside or when Escape key is pressed', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSearch={false}
      />
    )

    const toggleButton = screen.getByText('Select Options')

    await userEvent.click(toggleButton)
    expect(screen.queryByText('Option 1')).toBeInTheDocument()

    await userEvent.click(document.body)
    await waitFor(() =>
      expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
    )

    await userEvent.click(toggleButton)
    await userEvent.keyboard('[Escape]')

    await waitFor(() =>
      expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
    )
  })

  it('should toggle dropdown with keyboard accessibility', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSelectAllOptions={true}
        hasSearch={false}
      />
    )

    const toggleButton = screen.getByRole('button', { name: 'Select Options' })
    toggleButton.focus()

    await userEvent.keyboard('[Enter]')

    await waitFor(() =>
      expect(screen.getByText(/Tout sélectionner/i)).toBeInTheDocument()
    )

    await userEvent.keyboard('[Escape]')

    await waitFor(() =>
      expect(screen.queryByText(/Tout sélectionner/i)).not.toBeInTheDocument()
    )
  })
})

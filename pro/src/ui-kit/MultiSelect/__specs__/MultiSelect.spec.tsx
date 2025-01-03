import { render, screen, fireEvent, waitFor } from '@testing-library/react'
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
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the MultiSelect component with the correct initial selected options', () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        defaultOptions={defaultOptions}
      />
    )
    // Check that the initial selected options are rendered in the SelectedValuesTags
    expect(screen.getByText('Option 1')).toBeInTheDocument()
  })

  it('toggles the dropdown when the trigger is clicked', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSelectAllOptions={true}
      />
    )
    const toggleButton = screen.getByText('Select Options')
    await userEvent.click(toggleButton) // Open the dropdown
    expect(screen.getByText(/Tout sélectionner/i)).toBeInTheDocument()

    await userEvent.click(toggleButton) // Close the dropdown
    expect(screen.queryByText(/Tout sélectionner/i)).not.toBeInTheDocument()
  })

  it('selects all options when "Select All" is clicked', async () => {
    render(
      <MultiSelect
        options={options}
        label="Select Options"
        legend="Legend"
        hasSelectAllOptions={true}
      />
    )

    const toggleButton = screen.getByText('Select Options')
    await userEvent.click(toggleButton) // Open the dropdown

    const selectAllCheckbox = screen.getByLabelText(/Tout sélectionner/i)
    fireEvent.click(selectAllCheckbox) // Select all options

    // Verify that all options are selected
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
      />
    )

    // Initially, Option 1 is selected
    const selectedTag = screen.getByText('Option 1')
    await userEvent.click(selectedTag) // Remove Option 1
    expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
  })

  it('closes the dropdown when clicked outside or when Escape key is pressed', async () => {
    render(
      <MultiSelect options={options} label="Select Options" legend="Legend" />
    )

    const toggleButton = screen.getByText('Select Options')

    fireEvent.click(toggleButton) // Open the dropdown
    expect(screen.queryByText('Option 1')).toBeInTheDocument()

    // Simulate a click outside the dropdown
    fireEvent.click(document.body)
    await waitFor(() =>
      expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
    )

    fireEvent.click(toggleButton) // Open the dropdown again
    fireEvent.keyDown(toggleButton, { key: 'Escape' }) // Close with Escape key
    await waitFor(() =>
      expect(screen.queryByText('Option 1')).not.toBeInTheDocument()
    )
  })
})

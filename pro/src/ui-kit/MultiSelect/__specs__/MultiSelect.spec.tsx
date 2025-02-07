import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { MultiSelect, Options } from '../MultiSelect'

describe('<MultiSelect />', () => {
  const options = [
    { id: '1', label: 'Option 1' },
    { id: '2', label: 'Option 2' },
    { id: '3', label: 'Option 3' },
  ]

  const otherOptions = [
    { id: '4', label: 'Option 4' },
    { id: '5', label: 'Option 5' },
    { id: '6', label: 'Option 6' },
  ]

  const renderMultiSelect = ({
    hasSelectAllOptions = false,
    options,
  }: {
    hasSelectAllOptions?: boolean
    options: Options[]
  }) => {
    const defaultOptions = [{ id: '1', label: 'Option 1' }]

    return render(
      <MultiSelect
        options={options}
        label="Select Options"
        defaultOptions={defaultOptions}
        hasSearch={false}
        hasSelectAllOptions={hasSelectAllOptions}
        onSelectedOptionsChanged={(selectedOptions) => {
          return selectedOptions
        }}
        name="options"
        buttonLabel="Options"
      />
    )
  }

  it('should render correctly', () => {
    renderMultiSelect({ options: [{ options }] })

    expect(screen.getByRole('button', { name: 'Options' })).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderMultiSelect({ options: [{ options }] })

    expect(await axe(container)).toHaveNoViolations()

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the MultiSelect component with the correct initial selected options', () => {
    renderMultiSelect({ options: [{ options }] })

    const selectedTag = screen.getByRole('button', {
      name: 'Supprimer Option 1',
    })

    expect(selectedTag).toBeInTheDocument()
  })

  it('toggles the dropdown when the trigger is clicked', async () => {
    renderMultiSelect({ hasSelectAllOptions: true, options: [{ options }] })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    expect(selectAllCheckbox).toBeInTheDocument()

    await userEvent.click(toggleButton)

    expect(selectAllCheckbox).not.toBeInTheDocument()
  })

  it('selects all options when "Select All" is clicked', async () => {
    renderMultiSelect({ hasSelectAllOptions: true, options: [{ options }] })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    await userEvent.click(selectAllCheckbox)

    options.forEach((option) => {
      expect(screen.getByLabelText(option.label)).toBeChecked()
    })
  })

  it('removes an option from the selected items when clicked in SelectedValuesTags', async () => {
    renderMultiSelect({ options: [{ options }] })

    const selectedTag = screen.getByRole('button', {
      name: 'Supprimer Option 1',
    })

    await userEvent.click(selectedTag)

    expect(selectedTag).not.toBeInTheDocument()
  })

  it('closes the dropdown when clicked outside or when Escape key is pressed', async () => {
    renderMultiSelect({ options: [{ options }] })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    toggleButton.focus()

    await userEvent.click(toggleButton)

    const optionCheckbox2 = screen.getByRole('checkbox', { name: 'Option 1' })

    expect(optionCheckbox2).toBeInTheDocument()

    await userEvent.click(document.body)

    await waitFor(() => expect(optionCheckbox2).not.toBeInTheDocument())

    await userEvent.click(toggleButton)
    await userEvent.keyboard('[Escape]')

    await waitFor(() => expect(optionCheckbox2).not.toBeInTheDocument())
  })

  it('should toggle dropdown with keyboard accessibility', async () => {
    renderMultiSelect({ hasSelectAllOptions: true, options: [{ options }] })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    toggleButton.focus()

    await userEvent.keyboard('[Enter]')

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    await waitFor(() => expect(selectAllCheckbox).toBeInTheDocument())

    await userEvent.keyboard('[Escape]')

    await waitFor(() => expect(selectAllCheckbox).not.toBeInTheDocument())
  })

  it('should select/unselect all value of a specific option', async () => {
    renderMultiSelect({
      hasSelectAllOptions: true,
      options: [
        {
          options,
        },
        {
          options: otherOptions,
          hasSelectAllOptions: true,
          selectAllLabel: 'Other options',
        },
      ],
    })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    toggleButton.focus()

    await userEvent.click(toggleButton)

    const selectOtherOptionsCheckbox = screen.getByRole('checkbox', {
      name: 'Other options',
    })

    await waitFor(() => expect(selectOtherOptionsCheckbox).toBeInTheDocument())

    await userEvent.click(selectOtherOptionsCheckbox)

    otherOptions.forEach((option) => {
      expect(screen.getByLabelText(option.label)).toBeChecked()
    })

    await userEvent.click(selectOtherOptionsCheckbox)

    otherOptions.forEach((option) => {
      expect(screen.getByLabelText(option.label)).not.toBeChecked()
    })

  })
})

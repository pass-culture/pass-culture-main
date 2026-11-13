import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { MultiSelect, type Option } from '../MultiSelect'

describe('<MultiSelect />', () => {
  const options = [
    { id: '1', label: 'Option 1' },
    { id: '2', label: 'Option 2' },
    { id: '3', label: 'Option 3' },
  ]

  const renderMultiSelect = ({
    hasSelectAllOptions = false,
    options,
  }: {
    hasSelectAllOptions?: boolean
    options: Option[]
  }) => {
    const defaultOptions = [{ id: '1', label: 'Option 1' }]

    return render(
      <MultiSelect
        options={options}
        selectedOptions={options}
        label="Select Options"
        defaultOptions={defaultOptions}
        hasSearch={false}
        hasSelectAllOptions={hasSelectAllOptions}
        onSelectedOptionsChanged={(selectedOptions) => {
          return selectedOptions
        }}
        buttonLabel="Options"
      />
    )
  }

  it('should render correctly', () => {
    renderMultiSelect({ options })

    expect(screen.getByRole('button', { name: 'Options' })).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderMultiSelect({ options })

    expect(await axe(container)).toHaveNoViolations()

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the MultiSelect component with the correct initial selected options', () => {
    renderMultiSelect({ options })

    const selectedTag = screen.getByRole('button', {
      name: 'Supprimer Option 1',
    })

    expect(selectedTag).toBeInTheDocument()
  })

  it('toggles the dropdown when the trigger is clicked', async () => {
    renderMultiSelect({ hasSelectAllOptions: true, options })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    expect(selectAllCheckbox).toBeInTheDocument()

    await userEvent.click(toggleButton)

    expect(selectAllCheckbox).not.toBeInTheDocument()
  })

  it('opens a disclosure without moving focus and supports native checkbox keyboard navigation', async () => {
    const user = userEvent.setup()
    renderMultiSelect({ options })

    const trigger = screen.getByRole('button', { name: 'Options' })
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
    expect(trigger).not.toHaveAttribute('aria-haspopup')
    trigger.focus()
    await user.keyboard('[Enter]')

    const panel = screen.getByRole('group', { name: 'Options' })
    expect(panel).toHaveAttribute('id', trigger.getAttribute('aria-controls'))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(trigger).toHaveFocus()

    await user.tab()
    const firstOption = screen.getByRole('checkbox', { name: 'Option 1' })
    expect(firstOption).toHaveFocus()
    expect(firstOption).toBeChecked()
    await user.keyboard('[Space]')
    expect(firstOption).not.toBeChecked()
    await user.tab()
    expect(screen.getByRole('checkbox', { name: 'Option 2' })).toHaveFocus()

    await user.keyboard('[Escape]')
    expect(trigger).toHaveFocus()
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
    expect(panel).not.toBeInTheDocument()
  })

  it('allows tabbing out of the panel without trapping focus', async () => {
    const user = userEvent.setup()
    renderMultiSelect({ options })

    await user.click(screen.getByRole('button', { name: 'Options' }))
    await user.tab()
    await user.tab()
    await user.tab()
    expect(screen.getByRole('checkbox', { name: 'Option 3' })).toHaveFocus()

    await user.tab()
    expect(
      screen.getByRole('button', { name: 'Supprimer Option 1' })
    ).toHaveFocus()
    expect(screen.getByRole('button', { name: 'Options' })).toHaveAttribute(
      'aria-expanded',
      'false'
    )
  })

  it('selects all options when "Select All" is clicked', async () => {
    renderMultiSelect({ hasSelectAllOptions: true, options })

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    await userEvent.click(toggleButton)

    const selectAllCheckbox = screen.getByRole('checkbox', {
      name: 'Tout sélectionner',
    })

    await userEvent.click(selectAllCheckbox)

    options.forEach(async (option) => {
      await waitFor(() =>
        expect(screen.getByLabelText(option.label)).toBeChecked()
      )
    })
  })

  it('removes an option from the selected items when clicked in SelectedValuesTags', async () => {
    renderMultiSelect({ options })

    const selectedTag = screen.getByRole('button', {
      name: 'Supprimer Option 1',
    })

    await userEvent.click(selectedTag)

    expect(selectedTag).not.toBeInTheDocument()
  })

  it.each(['click', 'Enter', 'Space'])(
    'returns focus to the trigger after removing the last tag with %s',
    async (activation) => {
      const user = userEvent.setup()
      renderMultiSelect({ options })

      const trigger = screen.getByRole('button', { name: 'Options' })
      await user.tab()
      await user.tab()

      for (const [index, option] of options.entries()) {
        const tag = screen.getByRole('button', {
          name: `Supprimer ${option.label}`,
        })
        expect(tag).toHaveFocus()

        if (activation === 'click') {
          await user.click(tag)
        } else {
          await user.keyboard(`[${activation}]`)
        }

        expect(tag).not.toBeInTheDocument()
        if (index < options.length - 1) {
          expect(
            screen.getByRole('button', {
              name: `Supprimer ${options[index + 1].label}`,
            })
          ).toHaveFocus()
        }
      }

      expect(trigger).toHaveFocus()
      expect(trigger).toHaveAttribute('aria-expanded', 'false')
      expect(trigger).toHaveAccessibleDescription('0 élément sélectionné')
    }
  )

  it('keeps focus on the checkbox when deselecting the last option in the panel', async () => {
    const user = userEvent.setup()
    renderMultiSelect({ options: [options[0]] })

    const trigger = screen.getByRole('button', { name: 'Options' })
    await user.click(trigger)
    await user.tab()

    const checkbox = screen.getByRole('checkbox', { name: 'Option 1' })
    await user.keyboard('[Space]')

    expect(checkbox).not.toBeChecked()
    expect(checkbox).toHaveFocus()
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(
      screen.queryByRole('button', { name: 'Supprimer Option 1' })
    ).not.toBeInTheDocument()
  })

  it('closes the dropdown when clicked outside or when Escape key is pressed', async () => {
    renderMultiSelect({ options })

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
    renderMultiSelect({ hasSelectAllOptions: true, options })

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

  it('should not propagate the event when pressing the Escape key', async () => {
    const globalKeyDownMock = vi.fn()
    render(
      <div onKeyDown={globalKeyDownMock}>
        <MultiSelect
          options={[{ id: '1', label: 'Option 1' }]}
          buttonLabel="Options"
          label="label"
          hasSearch
          searchLabel="Input label"
          onSelectedOptionsChanged={() => {}}
        />
      </div>
    )

    const toggleButton = screen.getByRole('button', { name: 'Options' })
    toggleButton.focus()

    await userEvent.click(toggleButton)

    const searchInput = screen.getByLabelText('Input label')

    await userEvent.type(searchInput, '1')

    await userEvent.keyboard('{Escape}')

    //  Once for the search input value typed, and once for the Escape key
    expect(globalKeyDownMock).toHaveBeenCalledOnce()
  })
})

import { render, screen } from '@testing-library/react'
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

  const defaultOptions: Option[] = [{ id: '1', label: 'Option 1' }]

  const onOptionSelect = vi.fn()

  it('renders options with checkboxes', () => {
    render(
      <MultiSelectPanel
        options={options}
        label={''}
        onOptionSelect={function (option: Option | 'all' | undefined): void {
          throw new Error('Function not implemented.')
        }}
      />
    )

    expect(screen.getByLabelText('Option 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 2')).toBeInTheDocument()
    expect(screen.getByLabelText('Option 3')).toBeInTheDocument()
  })

  it('renders the search input if hasSearch is true', () => {
    render(
      <MultiSelectPanel
        options={[]}
        label={''}
        onOptionSelect={function (option: Option | 'all' | undefined): void {
          throw new Error('Function not implemented.')
        }}
        hasSearch={true}
        searchExample="Exemple: Nantes"
      />
    )

    expect(screen.getByText(/Exemple: Nantes/i)).toBeInTheDocument()
  })

  it('not renders the search input if hasSearch is false', () => {
    render(
      <MultiSelectPanel
        options={[]}
        label={''}
        onOptionSelect={function (option: Option | 'all' | undefined): void {
          throw new Error('Function not implemented.')
        }}
        hasSearch={false}
        searchExample="Exemple: Nantes"
      />
    )

    expect(screen.queryByText(/Exemple: Nantes/i)).not.toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <MultiSelectPanel
        options={[]}
        label={''}
        onOptionSelect={function (option: Option | 'all' | undefined): void {
          throw new Error('Function not implemented.')
        }}
        hasSearch={false}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('selects and deselects individual options', async () => {
    render(
      <MultiSelectPanel
        options={options}
        label=""
        onOptionSelect={onOptionSelect}
      />
    )

    // Initially, only Option 1 is selected
    const option2Checkbox = screen.getByLabelText(/Option 2/i)
    await userEvent.click(option2Checkbox) // Select Option 2
    expect(onOptionSelect).toHaveBeenCalledWith(options[1])

    await userEvent.click(option2Checkbox) // Deselect Option 2
    expect(onOptionSelect).toHaveBeenCalledWith(options[1])
  })
})

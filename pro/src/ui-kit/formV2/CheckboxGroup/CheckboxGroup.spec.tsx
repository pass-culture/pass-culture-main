import { render, screen } from '@testing-library/react'

import { CheckboxGroup } from './CheckboxGroup'

describe('CheckboxGroup', () => {
  it('should display the checkbox inputs', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', name: 'checkbox1' },
          { label: 'Checkbox 2', name: 'checkbox2' },
        ]}
        legend="Choose multiple options"
        name="group"
      />
    )

    expect(screen.getByRole('group', { name: 'Choose multiple options' }))

    expect(screen.getByLabelText('Checkbox 1'))
    expect(screen.getByLabelText('Checkbox 2'))
  })

  it('should show an asterisk if the group is required', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', name: 'checkbox1' },
          { label: 'Checkbox 2', name: 'checkbox2' },
        ]}
        legend="Choose multiple options"
        name="group"
        required
      />
    )

    expect(screen.getByRole('group', { name: 'Choose multiple options *' }))
  })

  it('should not show an asterisk if the group is required but we chose not to display it', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', name: 'checkbox1' },
          { label: 'Checkbox 2', name: 'checkbox2' },
        ]}
        legend="Choose multiple options"
        name="group"
        required
        asterisk={false}
      />
    )

    expect(screen.getByRole('group', { name: 'Choose multiple options' }))
  })

  it('should render the group withou a legend and with a describedBy reference', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', name: 'checkbox1' },
          { label: 'Checkbox 2', name: 'checkbox2' },
        ]}
        describedBy="my-id"
        name="group"
      />
    )

    expect(screen.getByRole('group')).toHaveAttribute(
      'aria-describedby',
      expect.stringContaining('my-id')
    )
  })

  it('should display an error message', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', name: 'checkbox1' },
          { label: 'Checkbox 2', name: 'checkbox2' },
        ]}
        describedBy="my-id"
        error="Error message"
        name="group"
      />
    )

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'

import { CheckboxGroup } from './CheckboxGroup'

describe('CheckboxGroup', () => {
  it('should display the checkbox inputs', () => {
    render(
      <CheckboxGroup
        group={[
          { label: 'Checkbox 1', checked: false, onChange: () => {} },
          { label: 'Checkbox 2', checked: false, onChange: () => {} },
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
          { label: 'Checkbox 1', checked: false, onChange: () => {} },
          { label: 'Checkbox 2', checked: false, onChange: () => {} },
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
          { label: 'Checkbox 1', checked: false, onChange: () => {} },
          { label: 'Checkbox 2', checked: false, onChange: () => {} },
        ]}
        legend="Choose multiple options"
        name="group"
        required
        asterisk={false}
      />
    )

    expect(screen.getByRole('group', { name: 'Choose multiple options' }))
  })

  it('should display an error message', () => {
    render(
      <CheckboxGroup
        legend="Group legend"
        group={[
          { label: 'Checkbox 1', checked: false, onChange: () => {} },
          { label: 'Checkbox 2', checked: false, onChange: () => {} },
        ]}
        error="Error message"
        name="group"
      />
    )

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })
})

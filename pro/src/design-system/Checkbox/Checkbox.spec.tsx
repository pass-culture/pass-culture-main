import { render, screen } from '@testing-library/react'

import { Checkbox, CheckboxProps } from './Checkbox'

const renderCheckbox = (props: CheckboxProps) => {
  render(<Checkbox {...props} />)
}

describe('Checkbox', () => {
  it('should display the input and the label of the checkbox', () => {
    renderCheckbox({
      label: 'Checkbox label',
      variant: 'default',
      checked: false,
      onChange: () => {},
    })
    expect(screen.getByLabelText('Checkbox label')).toBeInTheDocument()
    expect(screen.getByRole('checkbox')).toBeInTheDocument()
  })

  it('should display the description and an icon', () => {
    renderCheckbox({
      label: 'Checkbox label',
      description: 'Lorem ipsum',
      variant: 'detailed',
      checked: false,
      onChange: () => {},
      asset: {
        variant: 'image',
        src: '',
      },
    })
    expect(screen.getByText('Lorem ipsum')).toBeInTheDocument()
    expect(screen.getByRole('presentation')).toBeInTheDocument()
  })

  it('should display text on the right', () => {
    renderCheckbox({
      label: 'Checkbox label',
      description: 'Lorem ipsum',
      variant: 'detailed',
      checked: false,
      onChange: () => {},
      asset: {
        variant: 'text',
        text: 'Asset text',
      },
    })
    expect(screen.getByText('Asset text')).toBeInTheDocument()
  })

  it('should not show the collapsed content if the checkbox is not checked', () => {
    renderCheckbox({
      label: 'Checkbox label',
      description: 'Lorem ipsum',
      variant: 'detailed',
      checked: false,
      onChange: () => {},
      collapsed: <>Test collapsed</>,
    })
    expect(screen.queryByText('Test collapsed')).not.toBeInTheDocument()
  })

  it('should show the collapsed content if the checkbox is checked', () => {
    renderCheckbox({
      label: 'Checkbox label',
      description: 'Lorem ipsum',
      variant: 'detailed',
      collapsed: <>Test collapsed</>,
      checked: true,
      onChange: () => {},
    })
    expect(screen.getByText('Test collapsed')).toBeInTheDocument()
  })

  it('should be partially checked', () => {
    renderCheckbox({
      label: 'Checkbox label',
      variant: 'default',
      checked: true,
      indeterminate: true,
      onChange: () => {},
    })
    expect(
      screen.getByRole('checkbox', { name: 'Checkbox label' })
    ).toBePartiallyChecked()
  })
})

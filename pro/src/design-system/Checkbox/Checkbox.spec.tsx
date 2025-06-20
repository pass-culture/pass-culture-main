import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Checkbox, CheckboxProps } from './Checkbox'

const renderCheckbox = (props: CheckboxProps) => {
  return render(<Checkbox {...props} />)
}

describe('Checkbox', () => {
  it('should have an accessible structure', async () => {
    const { container } = renderCheckbox({
      label: 'Checkbox label',
      variant: 'default',
      checked: false,
      onChange: () => {},
    })

    expect(await axe(container)).toHaveNoViolations()
  })

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

  it('should show an asterisk if the field is required', () => {
    renderCheckbox({
      label: 'Checkbox label',
      variant: 'default',
      required: true,
      checked: false,
      onChange: () => {},
    })
    expect(
      screen.getByRole('checkbox', { name: 'Checkbox label *' })
    ).toBeInTheDocument()
  })

  it('should not show an asterisk if the field is required but hidden from the label', () => {
    renderCheckbox({
      label: 'Checkbox label',
      variant: 'default',
      required: true,
      asterisk: false,
      checked: false,
      onChange: () => {},
    })
    expect(
      screen.getByRole('checkbox', { name: 'Checkbox label' })
    ).toBeInTheDocument()
  })
})

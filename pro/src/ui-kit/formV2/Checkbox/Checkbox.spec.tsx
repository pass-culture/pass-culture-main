import { render, screen } from '@testing-library/react'

import { Checkbox, CheckboxProps } from './Checkbox'

const renderCheckbox = ({
  label = 'Accessible',
  name = 'accessible',
  ...props
}: Partial<CheckboxProps>) => {
  render(<Checkbox label={label} name={name} {...props} />)
}

describe('EmailSpellCheckInput', () => {
  it('should display an error if prop is set', () => {
    renderCheckbox({ error: 'This is an error' })
    expect(screen.getByText('This is an error')).toBeInTheDocument()
  })

  it('should hide footer if hideFooter is set, no matter if error prop is set', () => {
    renderCheckbox({ error: 'This is an error', hideFooter: true })
    expect(screen.queryByText('This is an error')).not.toBeInTheDocument()
  })
})

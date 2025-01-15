import { render, screen } from '@testing-library/react'

import { BaseCheckbox } from './BaseCheckbox'

describe('BaseCHeckbox', () => {
  it('should render a checkbox with a label', () => {
    render(<BaseCheckbox label="My label" checked onChange={() => {}} />)

    expect(screen.getByLabelText('My label')).toBeChecked()
  })

  it('should show the checkbox children when the input is checked', () => {
    render(
      <BaseCheckbox
        label="My label"
        checked
        onChange={() => {}}
        childrenOnChecked={<span>My child</span>}
      />
    )

    expect(screen.getByText('My child')).toBeInTheDocument()
  })

  it('should not show the checkbox children when the input is not checked', () => {
    render(
      <BaseCheckbox
        label="My label"
        onChange={() => {}}
        childrenOnChecked={<span>My child</span>}
      />
    )

    expect(screen.queryByText('My child')).not.toBeInTheDocument()
  })
})

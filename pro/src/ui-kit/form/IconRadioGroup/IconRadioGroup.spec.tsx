import { render, screen } from '@testing-library/react'

import { IconRadioGroup, IconRadioGroupProps } from './IconRadioGroup'

const defaultProps: IconRadioGroupProps = {
  group: [
    {
      label: 'Mécontent',
      icon: 'J',
      value: '1',
    },
    {
      label: 'Content',
      icon: <span>2</span>,
      value: '2',
    },
  ],
  legend: 'Legend',
  name: 'question',
  onChange: () => {},
  value: '1',
}

function renderIconRadioGroup(props: Partial<IconRadioGroupProps> = {}) {
  render(<IconRadioGroup {...defaultProps} {...props} />)
}

describe('IconRadioGroup', () => {
  it('should show the available options', () => {
    renderIconRadioGroup()

    expect(screen.getByLabelText('Content')).toBeInTheDocument()
    expect(screen.getByLabelText('Mécontent')).toBeInTheDocument()
  })

  it('should show the error message', () => {
    renderIconRadioGroup({ error: 'Error message' })

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('should show the asterisk if the field is required', () => {
    renderIconRadioGroup({ required: true })

    expect(screen.getByText('Legend *')).toBeInTheDocument()
  })

  it('should not show the asterisk if the field is required but the asterisk is disabled', () => {
    renderIconRadioGroup({ required: true, asterisk: false })

    expect(screen.queryByText('Legend *')).not.toBeInTheDocument()
  })
})

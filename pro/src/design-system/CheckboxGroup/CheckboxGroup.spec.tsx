import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import dog from '../assets/dog.jpg'
import type { CheckboxProps } from '../Checkbox/Checkbox'
import { CheckboxGroup } from './CheckboxGroup'

const baseOptions = [
  { label: 'Option 1', value: '1', checked: false, onChange: () => {} },
  { label: 'Option 2', value: '2', checked: false, onChange: () => {} },
  { label: 'Option 3', value: '3', checked: false, onChange: () => {} },
]

const detailedOptions: CheckboxProps[] = [
  {
    label: 'A',
    name: 'a',
    variant: 'detailed',
    asset: { variant: 'image', src: dog, size: 's' },
    checked: false,
    onChange: () => {},
  },
  {
    label: 'B',
    name: 'b',
    variant: 'detailed',
    asset: { variant: 'image', src: dog, size: 's' },
    checked: false,
    onChange: () => {},
  },
]

describe('CheckboxGroup', () => {
  describe('Rendering', () => {
    it('renders the label', () => {
      render(<CheckboxGroup label="My label" options={baseOptions} />)
      expect(screen.getByText('My label')).toBeInTheDocument()
    })

    it('renders the description when provided', () => {
      render(
        <CheckboxGroup label="Label" description="Desc" options={baseOptions} />
      )
      expect(screen.getByText('Desc')).toBeInTheDocument()
    })

    it('renders the error message when provided', () => {
      render(
        <CheckboxGroup label="Label" error="Error!" options={baseOptions} />
      )
      expect(screen.getByText('Error!')).toBeInTheDocument()
    })

    it('renders all options', () => {
      render(<CheckboxGroup label="Label" options={baseOptions} />)
      baseOptions.forEach((opt) => {
        expect(screen.getByText(opt.label)).toBeInTheDocument()
      })
    })
  })

  describe('Selection logic', () => {
    it('respects the value prop', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={[
            {
              label: 'Option 1',
              name: '1',
              checked: false,
              onChange: () => {},
            },
            { label: 'Option 2', name: '2', checked: true, onChange: () => {} },
          ]}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')

      expect(checkboxes[0]).not.toBeChecked()
      expect(checkboxes[1]).toBeChecked()
    })
  })

  it('should propagate the disabled state to all children', () => {
    render(<CheckboxGroup label="Label" options={baseOptions} disabled />)
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes[0]).toBeDisabled()
    expect(checkboxes[1]).toBeDisabled()
  })

  describe('Accessibility', () => {
    it('associates the description and error with aria-describedby', () => {
      render(
        <CheckboxGroup
          label="Label"
          description="Desc"
          error="Err"
          options={baseOptions}
        />
      )
      const group = screen.getByRole('group')
      const desc = screen.getByText('Desc')
      const err = screen.getByText('Err')
      expect(group.getAttribute('aria-describedby')).toContain(desc.id)
      expect(group.getAttribute('aria-describedby')).toContain(err.id)
    })

    it('renders error in a role="alert" container', () => {
      render(
        <CheckboxGroup label="Label" error="Error!" options={baseOptions} />
      )
      const alert = screen.getByRole('alert')
      expect(alert).toBeInTheDocument()
      expect(alert).toHaveTextContent('Error!')
    })

    it('is accessible (axe) for variant default', async () => {
      const { container } = render(
        <CheckboxGroup label="Label" options={baseOptions} />
      )
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('is accessible (axe) for variant detailed', async () => {
      const { container } = render(
        <CheckboxGroup
          label="Label"
          options={detailedOptions}
          variant="detailed"
        />
      )
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})

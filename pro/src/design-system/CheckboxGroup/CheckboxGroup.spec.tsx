import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import { noop } from '@/commons/utils/noop'

import dog from '../assets/dog.jpg'
import { CheckboxGroup, type CheckboxGroupOption } from './CheckboxGroup'

const baseOptions = [
  { label: 'Option 1', value: '1' },
  { label: 'Option 2', value: '2' },
  { label: 'Option 3', value: '3' },
]

const detailedOptions = [
  {
    label: 'A',
    value: 'a',
    variant: 'detailed',
    asset: { variant: 'image', src: dog },
  },
  {
    label: 'B',
    value: 'b',
    variant: 'detailed',
    asset: { variant: 'image', src: dog },
  },
] as const

describe('CheckboxGroup', () => {
  describe('Rendering', () => {
    it('renders the label', () => {
      render(
        <CheckboxGroup
          label="My label"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      expect(screen.getByText('My label')).toBeInTheDocument()
    })

    it('renders the description when provided', () => {
      render(
        <CheckboxGroup
          label="Label"
          description="Desc"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      expect(screen.getByText('Desc')).toBeInTheDocument()
    })

    it('renders the error message when provided', () => {
      render(
        <CheckboxGroup
          label="Label"
          error="Error!"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      expect(screen.getByText('Error!')).toBeInTheDocument()
    })

    it('renders all options', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      baseOptions.forEach((opt) => {
        expect(screen.getByText(opt.label)).toBeInTheDocument()
      })
    })

    it('throws if less than two options are provided', () => {
      vi.spyOn(console, 'error').mockImplementation(() => {})
      expect(() =>
        render(
          <CheckboxGroup
            label="Label"
            options={[{ label: 'One', value: '1' }]}
            value={[]}
            onChange={noop}
          />
        )
      ).toThrow()
    })
  })

  describe('Selection logic', () => {
    it('allows multiple options to be selected', async () => {
      const onChange = vi.fn()
      const value = ['1']
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={value}
          onChange={onChange}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes[0]).toBeChecked()
      expect(checkboxes[1]).not.toBeChecked()
      await userEvent.click(checkboxes[1])
      expect(onChange).toHaveBeenCalledWith(['1', '2'])
    })

    it('calls onChange with the correct values when an option is toggled', async () => {
      const onChange = vi.fn()
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={['1']}
          onChange={onChange}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')
      await userEvent.click(checkboxes[2])
      expect(onChange).toHaveBeenCalledWith(['1', '3'])
    })

    it('respects the value prop', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={['3']}
          onChange={noop}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes[2]).toBeChecked()
    })
  })

  describe('Props propagation', () => {
    it('propagates the disabled state to all children', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          disabled
          value={[]}
          onChange={noop}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')
      checkboxes.forEach((cb) => expect(cb).toBeDisabled())
    })

    it('propagates the error state to all children', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          error="Error!"
          value={[]}
          onChange={noop}
        />
      )
      const checkboxes = screen.getAllByRole('checkbox')
      checkboxes.forEach(async (cb) => {
        const label = cb.closest('label') // Because the aria-invalid is on the parent label, not the checkbox input
        await waitFor(() => {
          expect(label).toHaveAttribute('aria-invalid', 'true')
        })
      })
    })
  })

  describe('Accessibility', () => {
    it('has role="group" on the wrapper', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      expect(screen.getByRole('group')).toBeInTheDocument()
    })

    it('associates the label with aria-labelledby', () => {
      render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      const group = screen.getByRole('group')
      const label = screen.getByText('Label')
      expect(group).toHaveAttribute('aria-labelledby', label.id)
    })

    it('associates the description and error with aria-describedby', () => {
      render(
        <CheckboxGroup
          label="Label"
          description="Desc"
          error="Err"
          options={baseOptions}
          value={[]}
          onChange={noop}
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
        <CheckboxGroup
          label="Label"
          error="Error!"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      const alert = screen.getByRole('alert')
      expect(alert).toBeInTheDocument()
      expect(alert).toHaveTextContent('Error!')
    })

    it('is accessible (axe) for variant default', async () => {
      const { container } = render(
        <CheckboxGroup
          label="Label"
          options={baseOptions}
          value={[]}
          onChange={noop}
        />
      )
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('is accessible (axe) for variant detailed', async () => {
      const { container } = render(
        <CheckboxGroup
          label="Label"
          options={detailedOptions as unknown as CheckboxGroupOption[]}
          variant="detailed"
          value={[]}
          onChange={noop}
        />
      )
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})

import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import { noop } from '@/commons/utils/noop'

import dog from '../assets/dog.jpg'
import {
  CheckboxGroup,
  type CheckboxGroupOption,
  type CheckboxGroupProps,
} from './CheckboxGroup'

const baseOptions: CheckboxGroupOption[] = [
  { label: 'Option 1', onChange: noop, checked: false },
  { label: 'Option 2', onChange: noop, checked: false },
  { label: 'Option 3', onChange: noop, checked: false },
]

const detailedOptions: CheckboxGroupOption[] = [
  {
    label: 'A',
    asset: { variant: 'image', src: dog },
    checked: false,
    onChange: noop,
  },
  {
    label: 'B',
    asset: { variant: 'image', src: dog },
    checked: false,
    onChange: noop,
  },
]

const renderCheckboxGroup = ({
  options,
  ...props
}: {
  options: CheckboxGroupOption[]
} & Partial<CheckboxGroupProps>) => {
  return render(
    <CheckboxGroup label="My label" name="test" {...props} options={options} />
  )
}

describe('CheckboxGroup', () => {
  describe('Rendering', () => {
    it('renders the label', () => {
      renderCheckboxGroup({
        label: 'My label',
        options: baseOptions,
      })
      expect(screen.getByText('My label')).toBeInTheDocument()
    })

    it('renders the label with proper tag element', () => {
      renderCheckboxGroup({
        label: 'My label',
        options: baseOptions,
        labelTag: 'h2',
      })
      expect(screen.getByText('My label')).toBeInTheDocument()
      expect(screen.getByText('My label').tagName).toBe('H2')
    })

    it('renders the description when provided', () => {
      renderCheckboxGroup({
        description: 'Desc',
        options: baseOptions,
      })
      expect(screen.getByText('Desc')).toBeInTheDocument()
    })

    it('should not show an asterisk if the group is required but we chose not to display it', () => {
      renderCheckboxGroup({
        label: 'My label',
        required: true,
        asterisk: true,
        options: baseOptions,
      })
      expect(screen.getByText('My label *')).toBeInTheDocument()
    })

    it('renders the error message when provided', () => {
      renderCheckboxGroup({
        options: baseOptions,
        error: 'Error!',
      })
      expect(screen.getByText('Error!')).toBeInTheDocument()
    })

    it('renders all options', () => {
      renderCheckboxGroup({
        options: baseOptions,
      })
      baseOptions.forEach((opt) => {
        expect(screen.getByText(opt.label)).toBeInTheDocument()
      })
    })

    it('throws if less than two options are provided', () => {
      vi.spyOn(console, 'error').mockImplementation(() => {})
      expect(() =>
        renderCheckboxGroup({
          options: [{ label: 'One', checked: false, onChange: noop }],
        })
      ).toThrow()
    })

    it('renders with the correct checkboxes checked', () => {
      renderCheckboxGroup({
        label: 'Label',
        options: baseOptions.map((option, index) => ({
          ...option,
          checked: index === 1,
        })),
      })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes[0]).not.toBeChecked()
      expect(checkboxes[1]).toBeChecked()
      expect(checkboxes[2]).not.toBeChecked()
    })
  })

  describe('Props propagation', () => {
    it('propagates the disabled state to all children', () => {
      renderCheckboxGroup({
        label: 'Label',
        options: baseOptions,
        disabled: true,
      })
      const checkboxes = screen.getAllByRole('checkbox')
      checkboxes.forEach((cb) => {
        expect(cb).toBeDisabled()
      })
    })

    it('propagates the error state to all children', () => {
      renderCheckboxGroup({
        label: 'Label',
        error: 'Error!',
        options: baseOptions,
        disabled: true,
      })
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
    it('associates the label with aria-labelledby', () => {
      renderCheckboxGroup({
        label: 'Label',
        options: baseOptions,
      })
      const group = screen.getByRole('group')
      const label = screen.getByText('Label')
      expect(group).toHaveAttribute('aria-labelledby', label.id)
    })

    it('associates the description and error with aria-describedby', () => {
      renderCheckboxGroup({
        label: 'Label',
        description: 'Desc',
        error: 'Err',
        options: baseOptions,
      })
      const group = screen.getByRole('group')
      const desc = screen.getByText('Desc')
      const err = screen.getByText('Err')
      expect(group.getAttribute('aria-describedby')).toContain(desc.id)
      expect(group.getAttribute('aria-describedby')).toContain(err.id)
    })

    it('is accessible (axe) for variant default', async () => {
      const { container } = renderCheckboxGroup({
        options: detailedOptions,
        variant: 'default',
      })
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('is accessible (axe) for variant detailed', async () => {
      const { container } = renderCheckboxGroup({
        options: detailedOptions,
        variant: 'detailed',
      })
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})

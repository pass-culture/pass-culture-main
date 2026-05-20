import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { DatePicker } from './DatePicker'

describe('DatePicker', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render an input of type date', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
      />
    )

    expect(screen.getByLabelText('input label')).toBeInTheDocument()
  })

  it('should display an asterisk if the picker is required', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
        required
      />
    )

    expect(screen.getByLabelText('input label *')).toBeInTheDocument()
  })

  it('should not display an asterisk if the picker is required but we chose to hide it', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
        required
        requiredIndicator="hidden"
      />
    )

    expect(screen.getByLabelText('input label')).toBeInTheDocument()
  })

  it('should display an error message', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
        error="Error message"
      />
    )

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })
})

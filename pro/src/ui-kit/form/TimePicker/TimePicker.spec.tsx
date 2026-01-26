import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { TimePicker } from './TimePicker'

describe('TimePicker', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <TimePicker
        value="11:11"
        onChange={() => {}}
        label="input label"
        name="time"
      />
    )

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should render an input of type time', () => {
    render(
      <TimePicker
        value="11:11"
        onChange={() => {}}
        label="input label"
        name="time"
      />
    )

    expect(screen.getByLabelText('input label')).toBeInTheDocument()
  })

  it('should display an asterisk if the picker is required', () => {
    render(
      <TimePicker
        value="11:11"
        onChange={() => {}}
        label="input label"
        name="time"
        required
      />
    )

    expect(screen.getByLabelText(/input label/)).toBeInTheDocument()
  })

  it('should not display an asterisk if the picker is required but we chose to hide it', () => {
    render(
      <TimePicker
        value="11:11"
        onChange={() => {}}
        label="input label"
        name="time"
        required
        requiredIndicator="hidden"
      />
    )

    expect(screen.getByLabelText('input label')).toBeInTheDocument()
  })

  it('should display an error message', () => {
    render(
      <TimePicker
        value="11:11"
        onChange={() => {}}
        label="input label"
        name="time"
        error="Error message"
      />
    )

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })
})

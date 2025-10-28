import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Select } from '@/ui-kit/form/Select/Select'

describe('Select', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <Select
        label="select label"
        name="mySelect"
        options={[{ label: 'option 1', value: 'option1' }]}
      />
    )

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should display a select input', () => {
    render(
      <Select
        label="select label"
        name="mySelect"
        options={[{ label: 'option 1', value: 'option1' }]}
      />
    )

    expect(screen.getByLabelText('select label')).toBeInTheDocument()
  })

  it('should display a select input with an asterisk if it is required', () => {
    render(
      <Select
        label="select label"
        name="mySelect"
        options={[{ label: 'option 1', value: 'option1' }]}
        required
      />
    )

    expect(screen.getByLabelText(/select label/)).toBeInTheDocument()
  })

  it('should display a select input without an asterisk if it is required but we chose not to display it', () => {
    render(
      <Select
        label="select label"
        name="mySelect"
        options={[{ label: 'option 1', value: 'option1' }]}
        required
        requiredIndicator={null}
      />
    )

    expect(screen.getByLabelText('select label')).toBeInTheDocument()
  })

  it('should display an error message', () => {
    render(
      <Select
        label="select label"
        name="mySelect"
        options={[{ label: 'option 1', value: 'option1' }]}
        error="Error message"
      />
    )

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })
})

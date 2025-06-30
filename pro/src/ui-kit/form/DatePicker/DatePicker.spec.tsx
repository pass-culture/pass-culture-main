import { render, screen } from '@testing-library/react'

import { DatePicker } from './DatePicker'

describe('DatePicker', () => {
  it('should render an input of type date', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
      />
    )

    expect(screen.getByLabelText('input label'))
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

    expect(screen.getByLabelText('input label *'))
  })

  it('should not display an asterisk if the picker is required but we chose to hide it', () => {
    render(
      <DatePicker
        value="2025-11-22"
        onChange={() => {}}
        label="input label"
        name="name"
        required
        asterisk={false}
      />
    )

    expect(screen.getByLabelText('input label'))
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

    expect(screen.getByText('Error message'))
  })
})

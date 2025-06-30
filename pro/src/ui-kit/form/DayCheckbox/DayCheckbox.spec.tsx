import { render, screen } from '@testing-library/react'

import { DayCheckbox } from './DayCheckbox'

describe('DayCheckbox', () => {
  it('should display a checkbox input', () => {
    render(<DayCheckbox name="field" label="L" tooltipContent="Lundi" />)

    expect(screen.getByLabelText('Lundi')).toBeInTheDocument()
  })

  it('should display an error message', () => {
    render(
      <DayCheckbox
        name="field"
        label="L"
        tooltipContent="Lundi"
        error="error message"
      />
    )

    expect(screen.getByText('error message')).toBeInTheDocument()
  })
})

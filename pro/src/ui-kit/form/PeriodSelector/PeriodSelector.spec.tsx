import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { PeriodSelector } from './PeriodSelector'

describe('PeriodSelector', () => {
  const mockOnBeginningDateChange = vi.fn()
  const mockOnEndingDateChange = vi.fn()

  const renderPeriodSelector = (props = {}) => {
    return render(
      <PeriodSelector
        onBeginningDateChange={mockOnBeginningDateChange}
        onEndingDateChange={mockOnEndingDateChange}
        periodBeginningDate=""
        periodEndingDate=""
        {...props}
      />
    )
  }

  it('should render without accessibility violations', async () => {
    const { container } = renderPeriodSelector()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should call onBeginningDateChange and onEndingDateChange', async () => {
    renderPeriodSelector()

    await userEvent.type(
      screen.getByLabelText('Début de la période'),
      '2020-10-20'
    )

    await userEvent.type(
      screen.getByLabelText('Fin de la période'),
      '2020-12-24'
    )

    expect(mockOnBeginningDateChange).toHaveBeenCalledWith('2020-10-20')
    expect(mockOnEndingDateChange).toHaveBeenCalledWith('2020-12-24')
  })

  it('should render error messages and set aria-invalid when errors are provided', () => {
    renderPeriodSelector({
      errors: {
        beginningDate: 'La date de début est obligatoire',
        endingDate: 'La date de fin est obligatoire',
      },
    })

    const beginInput = screen.getByLabelText('Début de la période')
    const endInput = screen.getByLabelText('Fin de la période')

    expect(beginInput).toHaveAttribute('aria-invalid', 'true')
    expect(endInput).toHaveAttribute('aria-invalid', 'true')

    expect(screen.getByText('La date de début est obligatoire')).toBeVisible()
    expect(screen.getByText('La date de fin est obligatoire')).toBeVisible()
  })
})

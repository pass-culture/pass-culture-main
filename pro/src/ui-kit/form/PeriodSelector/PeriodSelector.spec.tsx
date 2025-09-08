import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { PeriodSelector } from './PeriodSelector'

describe('PeriodSelector', () => {
  const mockOnBeginningDateChange = vi.fn()
  const mockOnEndingDateChange = vi.fn()
  const renderPeriodSelector = () => {
    return render(
      <PeriodSelector
        onBeginningDateChange={mockOnBeginningDateChange}
        onEndingDateChange={mockOnEndingDateChange}
        periodBeginningDate=""
        periodEndingDate=""
      />
    )
  }

  it('should render without accessibility violations', async () => {
    const { container } = renderPeriodSelector()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should call on onBeginningDateChange and onEndingDateChange', async () => {
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
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import PeriodSelector from '../PeriodSelector'

describe('PeriodSelector', () => {
  const mockChangePeriodBeginningDateValue = jest.fn()
  const mockChangePeriodEndingDateValue = jest.fn()
  const renderPeriodSelector = () => {
    render(
      <PeriodSelector
        changePeriodBeginningDateValue={mockChangePeriodBeginningDateValue}
        changePeriodEndingDateValue={mockChangePeriodEndingDateValue}
        label="label"
      />
    )
  }

  it('should call on changePeriodBeginningDateValue and changePeriodEndingDateValue', async () => {
    renderPeriodSelector()

    const startingDateInput = screen.getByLabelText('Début de la période')
    await userEvent.click(startingDateInput)
    await userEvent.click(screen.getByText('10'))

    const endCalendar = screen.getByLabelText('Fin de la période')
    await userEvent.click(endCalendar)
    await userEvent.click(screen.getByText('10'))

    expect(mockChangePeriodBeginningDateValue).toHaveBeenCalledTimes(1)
    expect(mockChangePeriodEndingDateValue).toHaveBeenCalledTimes(1)
  })
})

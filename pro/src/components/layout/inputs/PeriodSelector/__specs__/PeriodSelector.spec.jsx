import '@testing-library/jest-dom'
import { fireEvent, within } from '@testing-library/react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import PeriodSelector from '../PeriodSelector'

describe('components | PeriodSelector', () => {
  it('should open second calendar when a date has been selected in first calendar', async () => {
    render(
      <PeriodSelector
        changePeriodBeginningDateValue={jest.fn()}
        changePeriodEndingDateValue={jest.fn()}
        label="label"
        todayDate={new Date('2021/10/14')}
      />
    )

    const startingDateWrapper = screen.getByTestId('period-filter-begin-picker')
    const startingDateInput = within(startingDateWrapper).getByLabelText(
      'début de la période'
    )

    expect(startingDateWrapper.children).toHaveLength(1)
    userEvent.click(startingDateInput)
    expect(startingDateWrapper.children).toHaveLength(2)

    const endDateWrapper = screen.getByTestId('period-filter-end-picker')
    const beginCalendar = startingDateWrapper.children[1]

    fireEvent.click(
      within(beginCalendar).getByLabelText(
        'Choose Thursday, October 21st, 2021'
      )
    )
    expect(endDateWrapper.children).toHaveLength(2)

    const endCalendar = endDateWrapper.children[1]

    fireEvent.click(
      within(endCalendar).getByLabelText('Choose Saturday, October 30th, 2021')
    )
    expect(endDateWrapper.children).toHaveLength(1)
  })
})

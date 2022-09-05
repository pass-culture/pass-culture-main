import '@testing-library/jest-dom'

import { fireEvent, within, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import PeriodSelector from '../PeriodSelector'

describe('components | PeriodSelector', () => {
  const mockChangePeriodBeginningDateValue = jest.fn()
  const mockChangePeriodEndingDateValue = jest.fn()
  const renderPeriodSelector = () => {
    return render(
      <PeriodSelector
        changePeriodBeginningDateValue={mockChangePeriodBeginningDateValue}
        changePeriodEndingDateValue={mockChangePeriodEndingDateValue}
        label="label"
        todayDate={new Date('2021/10/14')}
      />
    )
  }
  it('should open second calendar when a date has been selected in first calendar', async () => {
    renderPeriodSelector()
    const startingDateWrapper = screen.getByTestId('period-filter-begin-picker')
    const startingDateInput = within(startingDateWrapper).getByLabelText(
      'début de la période'
    )

    expect(startingDateWrapper.children).toHaveLength(1)
    await userEvent.click(startingDateInput)
    expect(startingDateWrapper.children).toHaveLength(2)
    const endDateWrapper = screen.getByTestId('period-filter-end-picker')
    const beginCalendar = startingDateWrapper.children[1]

    fireEvent.click(
      within(beginCalendar).getByLabelText('Choose jeudi 21 octobre 2021')
    )
    expect(endDateWrapper.children).toHaveLength(2)

    const endCalendar = endDateWrapper.children[1]

    fireEvent.click(
      within(endCalendar).getByLabelText('Choose samedi 30 octobre 2021')
    )
    expect(endDateWrapper.children).toHaveLength(1)
  })
  it('should call on changePeriodBeginningDateValue and changePeriodEndingDateValue', async () => {
    renderPeriodSelector()
    const startingDateWrapper = screen.getByTestId('period-filter-begin-picker')
    const startingDateInput = within(startingDateWrapper).getByLabelText(
      'début de la période'
    )

    await userEvent.click(startingDateInput)
    const beginCalendar = startingDateWrapper.children[1]
    const endDateWrapper = screen.getByTestId('period-filter-end-picker')

    fireEvent.click(
      within(beginCalendar).getByLabelText('Choose jeudi 21 octobre 2021')
    )

    const endCalendar = endDateWrapper.children[1]

    fireEvent.click(
      within(endCalendar).getByLabelText('Choose samedi 30 octobre 2021')
    )
    expect(mockChangePeriodBeginningDateValue).toHaveBeenCalledTimes(1)
    expect(mockChangePeriodEndingDateValue).toHaveBeenCalledTimes(1)
  })
})

import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { BaseTimePicker } from '../BaseTimePicker'
import { SuggestedTimeList } from '../types'

const renderBaseTimePicker = ({
  value = '',
  suggestedTimeList,
}: {
  value?: string
  suggestedTimeList?: SuggestedTimeList
} = {}) => {
  render(
    <Formik initialValues={{ time: value }} onSubmit={vi.fn()}>
      <BaseTimePicker
        name="time"
        suggestedTimeList={suggestedTimeList}
        value={value}
        onChange={vi.fn()}
      />
    </Formik>
  )
}

describe('BaseTimePicker', () => {
  it('should render a time input and a 15min interval datalist as default', () => {
    renderBaseTimePicker()

    const input = screen.getByPlaceholderText('HH:MM')
    expect(input).toBeInTheDocument()
    expect(input.tagName).toBe('INPUT')
    expect(input).toHaveAttribute('type', 'time')

    const datalist = screen.getByTestId('timepicker-datalist')
    expect(datalist).toBeInTheDocument()

    // Limits are 00:00 and 23:59
    const minSuggestedTime = screen.getByText('00:00')
    expect(minSuggestedTime).toBeInTheDocument()
    const maxSuggestedTime = screen.getByText('23:45')
    expect(maxSuggestedTime).toBeInTheDocument()

    // Available and unavailable times regarding the interval
    const nonSuggestedTime = screen.queryByText('23:59')
    expect(nonSuggestedTime).not.toBeInTheDocument()
    const surelySuggestedTime = screen.queryByText('00:15')
    expect(surelySuggestedTime).toBeInTheDocument()
  })

  it('shouldn’t render a datalist if an empty object for suggested list configuration is provided', () => {
    renderBaseTimePicker({ suggestedTimeList: {} })
    const datalist = screen.queryByTestId('timepicker-datalist')
    expect(datalist).not.toBeInTheDocument()
  })

  it('should render a custom datalist if a configuration is provided', () => {
    renderBaseTimePicker({
      suggestedTimeList: { interval: 30, min: '09:00', max: '17:00' },
    })

    const datalist = screen.getByTestId('timepicker-datalist')
    expect(datalist).toBeInTheDocument()

    // Limits are 09:00 and 17:00
    const minSuggestedTime = screen.getByText('09:00')
    expect(minSuggestedTime).toBeInTheDocument()
    const maxSuggestedTime = screen.getByText('17:00')
    expect(maxSuggestedTime).toBeInTheDocument()

    // Available and unavailable times regarding the interval
    const nonSuggestedTime = screen.queryByText('17:30')
    expect(nonSuggestedTime).not.toBeInTheDocument()
    const surelySuggestedTime = screen.queryByText('09:30')
    expect(surelySuggestedTime).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import TimePicker from '../TimePicker'

const renderTimePicker = (initialValue: string | Date | null | undefined) => {
  render(
    <Formik initialValues={{ time: initialValue }} onSubmit={jest.fn()}>
      <TimePicker name="time" label="Horaire" />
    </Formik>
  )
}

describe('TimePicker', () => {
  it('should render field', () => {
    renderTimePicker('')
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
  })

  const setNumberInputValue = [
    { initialValue: '', value: '20', expectedNumber: '20' },
    { initialValue: '', value: 'azer', expectedNumber: '' },
    { initialValue: '', value: 'AZER', expectedNumber: '' },
    { initialValue: '', value: '2fsqjk', expectedNumber: '2' },
    { initialValue: '', value: '2fs:qm0', expectedNumber: '2:0' },
    { initialValue: null, value: '20', expectedNumber: '20' },
    { initialValue: undefined, value: '20', expectedNumber: '20' },
    { initialValue: new Date(), value: '20', expectedNumber: '20' },
  ]
  it.each(setNumberInputValue)(
    'should complete input correctly',
    async ({ initialValue, value, expectedNumber }) => {
      renderTimePicker(initialValue)

      const timepicker = screen.getByLabelText('Horaire', {
        exact: false,
      })
      await userEvent.clear(timepicker)
      await userEvent.type(timepicker, value)
      expect(timepicker).toHaveValue(expectedNumber)
    }
  )
})

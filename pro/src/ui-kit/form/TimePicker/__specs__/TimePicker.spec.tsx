import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import TimePicker from '../TimePicker'

const renderTimePicker = () => {
  render(
    <Formik initialValues={{ time: '' }} onSubmit={jest.fn()}>
      <TimePicker name="time" label="Horaire" />
    </Formik>
  )
}

describe('TimePicker', () => {
  it('should render field', () => {
    renderTimePicker()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
  })

  const setNumberInputValue = [
    { value: '20', expectedNumber: '20' },
    { value: 'azer', expectedNumber: '' },
    { value: 'AZER', expectedNumber: '' },
    { value: '2fsqjk', expectedNumber: '2' },
    { value: '2fs:qm0', expectedNumber: '2:0' },
  ]
  it.each(setNumberInputValue)(
    'should complete input correctly',
    async ({ value, expectedNumber }) => {
      renderTimePicker()

      const timepicker = screen.getByLabelText('Horaire', {
        exact: false,
      })
      await userEvent.type(timepicker, value)
      expect(timepicker).toHaveValue(expectedNumber)
    }
  )
})

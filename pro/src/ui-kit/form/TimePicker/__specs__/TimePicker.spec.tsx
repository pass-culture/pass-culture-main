import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import TimePicker, { TimePickerProps } from '../TimePicker'

const renderTimePicker = ({
  onSubmit = jest.fn(),
}: {
  onSubmit?: () => void
} = {}) => {
  const initialValues = { price: '' }
  const props: TimePickerProps = {
    label: 'Horaire',
    name: 'datetime',
  }
  return render(
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      <TimePicker {...props} />
    </Formik>
  )
}

describe('TimePicker', () => {
  it('should render field', () => {
    renderTimePicker()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
  })
})

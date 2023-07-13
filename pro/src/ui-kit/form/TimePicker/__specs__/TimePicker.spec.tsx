import { render, screen } from '@testing-library/react'
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
})

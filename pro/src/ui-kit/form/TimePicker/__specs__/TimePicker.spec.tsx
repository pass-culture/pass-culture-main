import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { TimePicker } from '../TimePicker'
import { SuggestedTimeList } from '../types'

const renderTimePicker = (
  initialValue: string | Date | null | undefined,
  suggestedTimeList?: SuggestedTimeList
) => {
  render(
    <Formik initialValues={{ time: initialValue }} onSubmit={vi.fn()}>
      <TimePicker
        name="time"
        label="Horaire"
        suggestedTimeList={suggestedTimeList}
      />
    </Formik>
  )
}

describe('TimePicker', () => {
  it('should render field', () => {
    renderTimePicker('')
    expect(screen.getByLabelText('Horaire *')).toBeInTheDocument()
  })
})

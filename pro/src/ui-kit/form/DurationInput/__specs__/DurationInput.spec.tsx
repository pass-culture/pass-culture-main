import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import DurationInput, { DurationInputProps } from '../DurationInput'

const renderDurationInput = () => {
  const initialValues = { durationMinutes: '' }
  const props: DurationInputProps = {
    label: 'Durée',
    name: 'durationMinutes',
  }
  return render(
    <Formik initialValues={initialValues} onSubmit={jest.fn()}>
      <DurationInput {...props} />
    </Formik>
  )
}

describe('DurationInput', () => {
  it('should render field', () => {
    renderDurationInput()
    expect(screen.getByLabelText('Durée')).toBeInTheDocument()
  })

  const setDurationInputValue = [
    { value: '2', expectedDuration: '2:00' },
    { value: '02', expectedDuration: '2:00' },
    { value: '2:', expectedDuration: '2:00' },
    { value: '2:3', expectedDuration: '2:03' },
    { value: '2:30', expectedDuration: '2:30' },
    { value: ':30', expectedDuration: '0:30' },
    { value: ':3', expectedDuration: '0:03' },
    { value: 'A', expectedDuration: '' },
  ]
  it.each(setDurationInputValue)(
    'should complete input onBlur',
    async ({ value, expectedDuration }) => {
      renderDurationInput()

      const durationInput = screen.getByLabelText('Durée', {
        exact: false,
      })
      await userEvent.type(durationInput, value)
      await userEvent.tab()
      expect(durationInput).toHaveValue(expectedDuration)
    }
  )

  const durationToBeEmpty = ['A', 'b', 'AZSQD', 'abcd']
  it.each(durationToBeEmpty)(
    'should render empty field onChange',
    async value => {
      renderDurationInput()

      const durationInput = screen.getByLabelText('Durée', {
        exact: false,
      })
      await userEvent.type(durationInput, value)
      expect(durationInput).toHaveValue('')
    }
  )
})

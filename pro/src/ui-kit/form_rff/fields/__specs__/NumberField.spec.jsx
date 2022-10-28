import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'

import NumberField from '../NumberField'

describe('src | components | layout | form | NumberField', () => {
  const renderNumberFields = (initialValues, handleOnSubmit) => {
    return render(
      <Form
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
        render={({ handleSubmit }) => (
          <form>
            <NumberField name="bar" />
            <NumberField name="foo" />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )
  }
  it('should submit a form with number field when number is a decimal with a dot', async () => {
    // given
    const initialValues = {
      bar: '3',
      foo: '5.6',
    }
    renderNumberFields(initialValues, handleOnSubmit)
    // when
    const barInput = screen.getAllByRole('spinbutton')[0]
    await userEvent.clear(barInput)
    await userEvent.type(barInput, '6')

    await userEvent.click(screen.getByRole('button'))

    // then
    function handleOnSubmit(formValues) {
      expect(formValues.bar).toBe(6)
      expect(formValues.foo).toStrictEqual(initialValues.foo)
    }
  })

  it('should submit a form with number field when number is a decimal with a comma', async () => {
    // given
    const initialValues = {
      bar: '3',
      foo: '5,6',
    }
    renderNumberFields(initialValues, handleOnSubmit)
    const barInput = screen.getAllByRole('spinbutton')[0]
    await userEvent.clear(barInput)
    await userEvent.type(barInput, '6')

    await userEvent.click(screen.getByRole('button'))
    // then
    function handleOnSubmit(formValues) {
      expect(formValues.bar).toBe(6)
      expect(formValues.foo).toStrictEqual(initialValues.foo)
    }
  })
})

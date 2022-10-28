import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'

import TextField from '../TextField'

describe('src | components | layout | form | TextField', () => {
  it('should submit a form with a title text field', async () => {
    // given
    const initialValues = {
      text: 'Ca parle de canapés.',
      title: 'J’irai droit au Conforama',
    }
    render(
      <Form
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
        render={({ handleSubmit }) => (
          <form>
            <TextField name="title" />
            <TextField name="text" />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    const textInput = screen.getAllByRole('textbox')[0]
    await userEvent.clear(textInput)
    await userEvent.type(textInput, 'J’irai droit au But')
    await userEvent.click(screen.getByRole('button'))
    // when

    // then
    function handleOnSubmit(formValues) {
      expect(formValues.title).toBe('J’irai droit au But')
      expect(formValues.text).toStrictEqual(initialValues.text)
    }
  })
})

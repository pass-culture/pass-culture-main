import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'

import HiddenField from '../HiddenField'
import TextField from '../TextField'

describe('src | components | layout | form | HiddenField', () => {
  it('should submit a form with a title text field', async () => {
    // given
    const initialValues = {
      subtitle: 'Mais jamais sans mon cadis.',
      title: 'J’irai droit au Conforama',
    }
    render(
      <Form
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
        render={({ handleSubmit }) => (
          <form>
            <TextField name="title" />
            <HiddenField name="subtitle" />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    const textInput = screen.getByRole('textbox')
    await userEvent.clear(textInput)
    await userEvent.type(textInput, 'J’irai droit au But')
    await userEvent.click(screen.getByRole('button'))

    // then
    function handleOnSubmit(formValues) {
      expect(formValues.title).toBe('J’irai droit au But')
      expect(formValues.subtitle).toStrictEqual(initialValues.subtitle)
    }
  })
})

import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import TextInput from '../TextInput'

describe('TextInput', () => {
  it.each([
    'text',
    'number',
    'email',
    'url',
    'password',
    'tel',
    'search',
  ] as const)(
    'should allow tabbing from one input of type %s to the next',
    async (inputType) => {
      render(
        <Formik initialValues={{ test1: '', test2: '' }} onSubmit={() => {}}>
          <>
            <TextInput type={inputType} label="Input 1" name="test1" />
            <TextInput type={inputType} label="Input 2" name="test2" />
          </>
        </Formik>
      )

      screen.getByLabelText('Input 1 *').focus()
      expect(screen.getByLabelText('Input 1 *')).toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).not.toHaveFocus()

      await userEvent.tab()
      expect(screen.getByLabelText('Input 1 *')).not.toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).toHaveFocus()
    }
  )
})

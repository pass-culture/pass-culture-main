import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { TextInput } from '../TextInput'

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

  it('should link the input to its description when defined', () => {
    const inputName = 'test'
    const inputLabel = 'Ceci est un champ texte'
    const descriptionContent = 'Instructions pour le remplissage du champ.'
    const descriptionId = `description-${inputName}`

    render(
      <Formik initialValues={{ test1: '', test2: '' }} onSubmit={() => {}}>
        <TextInput
          type="text"
          label={inputLabel}
          description={descriptionContent}
          name={inputName}
          isOptional={true}
        />
      </Formik>
    )

    const description = screen.queryByTestId(descriptionId)
    expect(description).toBeInTheDocument()
    expect(description).toHaveTextContent(descriptionContent)

    const input = screen.getByRole('textbox', { name: inputLabel })
    expect(input.getAttribute('aria-describedby')).toBe(descriptionId)
  })
})

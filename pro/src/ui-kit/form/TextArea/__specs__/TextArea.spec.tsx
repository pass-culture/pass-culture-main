import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'

import { TextArea } from '../TextArea'

describe('TextArea', () => {
  it('should link the input to its description when defined', () => {
    const inputName = 'test'
    const inputLabel = 'Ceci est un champ texte'
    const descriptionContent = 'Instructions pour le remplissage du champ.'
    const descriptionId = `description-${inputName}`

    render(
      <Formik initialValues={{ test1: '', test2: '' }} onSubmit={() => {}}>
        <TextArea
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

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'

import { TextArea } from '../TextArea'

const mockOnPressTemplateButton = vi.fn()

describe('TextArea', () => {
  const inputName = 'test'
  const inputLabel = 'Ceci est un champ texte'
  const descriptionContent = 'Instructions pour le remplissage du champ.'
  const descriptionId = `description-${inputName}`
  const wordingTemplate = 'wording template text'

  it('should link the input to its description when defined', () => {
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
    expect(input.getAttribute('aria-describedby')).toContain(descriptionId)
  })

  it('should display template button and template text onclick when A/B template is enabled', async () => {
    render(
      <Formik initialValues={{ test1: '', test2: '' }} onSubmit={() => {}}>
        <TextArea
          label={inputLabel}
          name={inputName}
          isOptional={true}
          wordingTemplate={wordingTemplate}
          hasTemplateButton={true}
          onPressTemplateButton={mockOnPressTemplateButton}
        />
      </Formik>
    )

    const templateButton = screen.getByRole('button', {
      name: 'Générer un modèle',
    })
    await userEvent.click(templateButton)

    const textarea = screen.getByRole('textbox', { name: inputLabel })
    expect(textarea).toHaveValue(wordingTemplate)
  })

  it('should call tracker when clicking on template button', async () => {
    render(
      <Formik initialValues={{ test1: '', test2: '' }} onSubmit={() => {}}>
        <TextArea
          label={inputLabel}
          name={inputName}
          isOptional={true}
          wordingTemplate={wordingTemplate}
          hasTemplateButton={true}
          onPressTemplateButton={mockOnPressTemplateButton}
        />
      </Formik>
    )

    const templateButton = screen.getByRole('button', {
      name: 'Générer un modèle',
    })
    await userEvent.click(templateButton)

    expect(mockOnPressTemplateButton).toHaveBeenCalledTimes(1)
  })
})

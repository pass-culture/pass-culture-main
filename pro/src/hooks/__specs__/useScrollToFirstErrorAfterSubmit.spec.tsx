import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik, Form } from 'formik'
import * as yup from 'yup'

import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { SubmitButton, TextInput } from 'ui-kit'

const scrollIntoViewMock = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

const TestForm = () => {
  useScrollToFirstErrorAfterSubmit()

  return (
    <Form>
      <TextInput name="test" label="test" />
      <SubmitButton />
    </Form>
  )
}

const TestComponent = () => {
  return (
    <Formik
      initialValues={{
        test: '',
      }}
      validationSchema={yup.object().shape({
        test: yup.string().required('Veuillez remplir le champ'),
      })}
      onSubmit={vi.fn()}
    >
      <TestForm />
    </Formik>
  )
}

const renderUseScrollToFirstErrorAfterSubmit = () => {
  return render(<TestComponent />)
}

describe('useScrollToFirstErrorAfterSubmit', () => {
  it('should scroll into view and give focus', async () => {
    Element.prototype.scrollIntoView = scrollIntoViewMock

    renderUseScrollToFirstErrorAfterSubmit()
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await waitFor(() => {
      expect(screen.getByText('Veuillez remplir le champ')).toBeInTheDocument()
    })
    expect(scrollIntoViewMock).toHaveBeenCalled()
    expect(screen.getByLabelText('test')).toHaveFocus()
  })
})

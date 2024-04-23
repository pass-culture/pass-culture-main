import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik, Form } from 'formik'
import * as yup from 'yup'

import { TextInput } from 'ui-kit'
import { SubmitButton } from 'ui-kit/SubmitButton/SubmitButton'

import { ScrollToFirstErrorAfterSubmit } from '../ScrollToFirstErrorAfterSubmit'

const scrollIntoViewMock = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

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
      <Form>
        <TextInput name="test" label="test" />
        <SubmitButton />

        <ScrollToFirstErrorAfterSubmit />
      </Form>
    </Formik>
  )
}

const renderScrollToFirstErrorAfterSubmit = () => {
  return render(<TestComponent />)
}

describe('ScrollToFirstErrorAfterSubmit', () => {
  it('should scroll into view and give focus', async () => {
    Element.prototype.scrollIntoView = scrollIntoViewMock

    renderScrollToFirstErrorAfterSubmit()
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await waitFor(() => {
      expect(screen.getByText('Veuillez remplir le champ')).toBeInTheDocument()
    })
    expect(scrollIntoViewMock).toHaveBeenCalled()
    expect(screen.getByLabelText('test *')).toHaveFocus()
  })
})

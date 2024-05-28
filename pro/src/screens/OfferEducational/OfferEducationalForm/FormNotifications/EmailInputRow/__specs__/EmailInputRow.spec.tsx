import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { EmailInputRow } from '../EmailInputRow'

describe('EmailInputRow', () => {
  it('should render trash icon by default', () => {
    render(
      <Formik initialValues={{}} onSubmit={vi.fn()}>
        <EmailInputRow disableForm={false} name={`email`} key={`email`} />
      </Formik>
    )
    const removeInputIcon = screen.getByRole('button', {
      name: 'Supprimer l’email',
    })
    expect(removeInputIcon).toBeInTheDocument()
  })
})

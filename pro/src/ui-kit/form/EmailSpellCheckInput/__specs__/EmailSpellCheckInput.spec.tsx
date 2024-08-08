import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { EmailSpellCheckInput } from '../EmailSpellCheckInput'

vi.mock('libphonenumber-js', () => {
  return {
    ...vi.importActual('libphonenumber-js'),
    parsePhoneNumberFromString: vi.fn(),
  }
})

const renderEmailSpellCheckInput = () => {
  render(
    <Formik
      initialValues={{ email: '' }}
      onSubmit={() => {}}
      validationSchema={yup.string().required().email()}
    >
      <EmailSpellCheckInput
        name="email"
        label="Email"
        description="Format : mail@exemple.com"
      />
    </Formik>
  )
}

describe('EmailSpellCheckInput', () => {
  it('The email suggestion should not be displayed when the field is empty', async () => {
    renderEmailSpellCheckInput()
    const emailField = screen.getByLabelText('Email *')
    await userEvent.click(emailField)
    await userEvent.tab()
    expect(
      screen.queryByText(/Voulez-vous plutôt dire/)
    ).not.toBeInTheDocument()
  })

  it('The email suggestion should not be displayed when the field is invalid', async () => {
    renderEmailSpellCheckInput()
    const emailField = screen.getByLabelText('Email *')
    await userEvent.click(emailField)
    await userEvent.type(emailField, 'this is not an email')
    await userEvent.tab()
    expect(
      screen.queryByText(/Voulez-vous plutôt dire/)
    ).not.toBeInTheDocument()
  })

  it('The email suggestion should not be displayed when the email is already valid', async () => {
    renderEmailSpellCheckInput()
    const emailField = screen.getByLabelText('Email *')
    await userEvent.click(emailField)
    await userEvent.type(emailField, 'email@exemple.com')
    await userEvent.tab()
    expect(
      screen.queryByText(/Voulez-vous plutôt dire/)
    ).not.toBeInTheDocument()
  })

  it('The email suggestion should be displayed when the email is invalid', async () => {
    renderEmailSpellCheckInput()
    const emailField = screen.getByLabelText('Email *')
    await userEvent.click(emailField)
    await userEvent.type(emailField, 'email@gmil.com')
    await userEvent.tab()
    await waitFor(() => {
      expect(screen.getByText(/Voulez-vous plutôt dire/)).toBeInTheDocument()
    })
  })

  it('The apply button should change the email value', async () => {
    renderEmailSpellCheckInput()
    const emailField = screen.getByLabelText('Email *')
    await userEvent.click(emailField)
    await userEvent.type(emailField, 'email@gmil.com')
    await userEvent.tab()
    const applyButton = screen.getByText(/Appliquer la modification/)
    expect(applyButton).toHaveFocus()

    await userEvent.keyboard('{enter}')

    await waitFor(() => {
      expect(
        screen.queryByText(/Voulez-vous plutôt dire/)
      ).not.toBeInTheDocument()
    })
    expect(emailField).toHaveValue('email@gmail.com')
  })
})

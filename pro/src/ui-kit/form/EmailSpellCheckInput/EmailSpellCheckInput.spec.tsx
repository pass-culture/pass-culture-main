import { yupResolver } from '@hookform/resolvers/yup'
import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { emailSchema } from 'commons/utils/isValidEmail'
import { FormProvider, useForm } from 'react-hook-form'
import * as yup from 'yup'

import { EmailSpellCheckInput } from './EmailSpellCheckInput'

// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo to work
type WrapperFormValues = { email: string }
const FormWrapper = () => {
  const hookForm = useForm<WrapperFormValues>({
    resolver: yupResolver(
      yup.object().shape({ email: yup.string().required().test(emailSchema) })
    ),
  })

  const { register, setValue } = hookForm

  return (
    <FormProvider {...hookForm}>
      <EmailSpellCheckInput
        {...register('email')}
        label="Email"
        required={true}
        asterisk={true}
        description="Format : mail@exemple.com"
        onApplyTip={(tip) => {
          setValue('email', tip)
        }}
      />
    </FormProvider>
  )
}

const renderEmailSpellCheckInput = () => {
  render(<FormWrapper />)
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

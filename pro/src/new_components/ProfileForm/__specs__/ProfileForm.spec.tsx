// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import * as yup from 'yup'

import { Banner, TextInput } from 'ui-kit'
import { render, screen } from '@testing-library/react'

import { IProfileFormProps } from '../ProfileForm'
import { ProfileForm } from '../'
import React from 'react'
import userEvent from '@testing-library/user-event'

const defaultFields = [
  <TextInput label="Prénom" name="firstName" />,
  <TextInput label="Nom" name="lastName" />,
]

const defaultSchema = yup.object().shape({
  firstName: yup.string().max(128).required(),
  lastName: yup.string().max(128).required(),
})

const onProfileFormSubmit = jest.fn()

const renderProfileForm = (props: IProfileFormProps) => {
  return render(<ProfileForm {...props} />)
}

describe('new_components:ProfileForm', () => {
  let props: IProfileFormProps
  beforeEach(() => {
    props = {
      title: 'What are you?',
      subtitle: 'A bird',
      fields: defaultFields,
      validationSchema: defaultSchema,
      initialValues: {
        firstName: 'FirstName',
        lastName: 'lastName',
      },
      banner: <Banner>Banner test text</Banner>,
      shouldDisplayBanner: false,
      onFormSubmit: onProfileFormSubmit,
    }
  })
  it('renders component successfully', () => {
    renderProfileForm(props)
    const element = screen.getByTestId(/test-profile-form/i)
    expect(element).toBeInTheDocument()
  })
  it('should toggle a slider when editing / closing the form', async () => {
    renderProfileForm(props)
    const editButton = screen.getByText('Modifier')
    await userEvent.click(editButton)
    expect(editButton).not.toBeInTheDocument()
    const fields = screen.getAllByRole('textbox')
    expect(fields.length).toEqual(2)
    await userEvent.click(screen.getByText('Annuler'))
    expect(screen.getByText('Modifier')).toBeInTheDocument()
  })
  it('should trigger onSubmit callback when submitting', async () => {
    renderProfileForm(props)
    await userEvent.click(screen.getByText('Modifier'))
    await userEvent.type(screen.getByLabelText('Prénom'), 'Harry')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    await expect(onProfileFormSubmit).toHaveBeenCalledTimes(1)
  })
  it('should render a banner when shouldDisplayBanner', async () => {
    props.shouldDisplayBanner = true
    renderProfileForm(props)
    const bannerText = screen.getByText('Banner test text')
    expect(bannerText).toBeInTheDocument()
    await userEvent.click(screen.getByText('Modifier'))
    expect(bannerText).not.toBeInTheDocument()
  })
})

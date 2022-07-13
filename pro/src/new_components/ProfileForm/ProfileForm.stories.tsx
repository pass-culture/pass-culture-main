import * as yup from 'yup'

import { ProfileForm } from './'
import React from 'react'
import { ResetEmailBanner } from 'new_components/Banner'
// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction
import { Story } from '@storybook/react'
import { TextInput } from 'ui-kit'

type Props = React.ComponentProps<typeof ProfileForm>

const fields = [
  <TextInput label="Prénom" name="firstName" />,
  <TextInput label="Nom" name="lastName" />,
]

const validationSchema = yup.object().shape({
  firstName: yup.string().max(128).required(),
  lastName: yup.string().max(128).required(),
})

const onFormSubmit = (values: any) => {
  alert(Object.values(values))
}

const Template: Story<Props> = args => <ProfileForm {...args} />

export const BasicProfileForm = Template.bind({})
BasicProfileForm.storyName = 'Basic Form'
BasicProfileForm.args = {
  title: 'Are you a wizard ?',
  subtitle: 'Harry Potter',
  fields: fields,
  onFormSubmit: onFormSubmit,
  validationSchema: validationSchema,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
}

export const BanneredProfileForm = Template.bind({})
BanneredProfileForm.storyName = 'Bannered Form'
BanneredProfileForm.args = {
  title: 'Are you a wizard ?',
  subtitle: 'Harry Potter',
  fields: fields,
  onFormSubmit: onFormSubmit,
  validationSchema: validationSchema,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
  shouldDisplayBanner: true,
  banner: <ResetEmailBanner email="harry.socier15ans@poudlar.com" />,
}

export default {
  title: 'components/ProfileForm',
}

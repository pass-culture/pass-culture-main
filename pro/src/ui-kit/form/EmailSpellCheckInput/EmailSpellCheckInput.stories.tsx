import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import { IEmailSpellCheckInputProps } from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'
import { EmailSpellCheckInput } from 'ui-kit/form/index'

export default {
  title: 'ui-kit/forms/EmailSpellCheckInput',
  component: EmailSpellCheckInput,
}
type Args = IEmailSpellCheckInputProps<any>

const Template: Story<Args> = args => (
  <Formik initialValues={{}} onSubmit={() => {}}>
    <EmailSpellCheckInput {...args} />
  </Formik>
)

const defaultProps: Args = {
  name: 'email',
  label: 'Adresse email',
  placeholder: 'email@exemple.com',
  overrideInitialTip: 'marie.dupont@gmail.com',
}

export const Default = Template.bind({})
Default.args = defaultProps

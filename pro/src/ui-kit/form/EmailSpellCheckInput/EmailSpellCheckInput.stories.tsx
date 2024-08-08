import { Formik } from 'formik'
import React from 'react'

import { EmailSpellCheckInput } from './EmailSpellCheckInput'

export default {
  title: 'ui-kit/forms/EmailSpellCheckInput',
  component: EmailSpellCheckInput,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ email: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const Default = {
  args: {
    name: 'email',
    label: 'Adresse email',
    description: 'Format: email@exemple.com',
    overrideInitialTip: 'marie.dupont@gmail.com',
  },
}

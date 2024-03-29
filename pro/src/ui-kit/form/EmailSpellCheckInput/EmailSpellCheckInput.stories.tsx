import { Formik } from 'formik'
import React from 'react'

import { EmailSpellCheckInput } from 'ui-kit/form/index'

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
    placeholder: 'email@exemple.com',
    overrideInitialTip: 'marie.dupont@gmail.com',
  },
}

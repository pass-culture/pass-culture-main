import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DurationInput from './DurationInput'
import { validationSchema } from './validationSchema'

export default {
  title: 'ui-kit/forms/DurationInput',
  component: DurationInput,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{ initialValues: { durationMinutes: '' } }}
        validationSchema={validationSchema}
        onSubmit={() => {}}
      >
        <Story />
      </Formik>
    ),
  ],
}

export const Default: StoryObj<typeof DurationInput> = {
  args: {
    name: 'durationMinutes',
    label: 'Durée',
  },
}

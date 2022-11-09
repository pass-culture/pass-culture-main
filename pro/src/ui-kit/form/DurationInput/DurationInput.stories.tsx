import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import DurationInput from './DurationInput'
import type { IDurationInputProps } from './DurationInput'

export default {
  title: 'ui-kit/forms/DurationInput',
  component: DurationInput,
}
interface Args extends IDurationInputProps {
  initialValues: { durationMinutes: string | null }
}

const args = {
  initialValues: { durationMinutes: '' },
  name: 'durationMinutes',
}

const validationSchema = yup.object().shape({
  durationMinutes: yup
    .string()
    .trim()
    .matches(
      /^[0-9]{1,3}:[0-9]{2}$/,
      'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
    ),
})

const Template: Story<Args> = args => (
  <Formik
    initialValues={args.initialValues}
    validationSchema={validationSchema}
    onSubmit={() => {}}
  >
    <DurationInput {...args} />
  </Formik>
)

export const WithoutLabel = Template.bind({})
WithoutLabel.args = args

export const WithLabel = Template.bind({})
WithLabel.args = {
  ...args,
  label: 'Durée',
}

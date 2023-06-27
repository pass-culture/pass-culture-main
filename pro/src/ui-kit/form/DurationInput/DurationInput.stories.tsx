import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DurationInput from './DurationInput'
import type { DurationInputProps } from './DurationInput'
import { validationSchema } from './validationSchema'

export default {
  title: 'ui-kit/forms/DurationInput',
  component: DurationInput,
}
interface Args extends DurationInputProps {
  initialValues: { durationMinutes: string | null }
}

const initialValues = { initialValues: { durationMinutes: '' } }
const args = {
  name: 'durationMinutes',
}

const Template: Story<Args> = args => (
  <Formik
    initialValues={initialValues}
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

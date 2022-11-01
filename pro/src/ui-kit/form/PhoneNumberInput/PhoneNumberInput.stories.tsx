import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import PhoneNumberInput, { PhoneNumberInputProps } from './PhoneNumberInput'

export default {
  title: 'ui-kit/forms/PhoneNumberInput',
  component: PhoneNumberInput,
}

const Template: Story<PhoneNumberInputProps> = args => (
  <Formik initialValues={{}} onSubmit={() => {}}>
    <PhoneNumberInput {...args} />
  </Formik>
)

export const Default = Template.bind({})
Default.args = { name: 'phone' }

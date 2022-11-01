import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import PhoneNumberInput, { PhoneNumberInputProps } from './PhoneNumberInput'

export default {
  title: 'ui-kit/forms/PhoneNumberInput',
  component: PhoneNumberInput,
}

const Template: Story<
  PhoneNumberInputProps & { initialValues: { phone?: string } }
> = args => (
  <Formik initialValues={args.initialValues} onSubmit={() => {}}>
    <PhoneNumberInput {...args} />
  </Formik>
)

export const Default = Template.bind({})
Default.args = { name: 'phone', initialValues: {} }

export const WithInitialValue = Template.bind({})
WithInitialValue.args = {
  name: 'phone',
  initialValues: { phone: '06 94 20 12 34' },
}

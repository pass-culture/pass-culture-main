import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import PhoneNumberInput from './PhoneNumberInput'

export default {
  title: 'ui-kit/forms/PhoneNumberInput',
  component: PhoneNumberInput,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ phone: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const Default: StoryObj<typeof PhoneNumberInput> = {
  args: {
    name: 'phone',
    label: 'Custom label for my required field',
  },
}

export const WithOptional: StoryObj<typeof PhoneNumberInput> = {
  args: {
    name: 'phone',
    label: 'Phone number input optional',
    isOptional: true,
  },
}

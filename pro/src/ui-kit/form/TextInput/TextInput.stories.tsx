import type { Meta, StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { TextInput } from './TextInput'

const meta: Meta<typeof TextInput> = {
  title: 'ui-kit/forms/TextInput',
  component: TextInput,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ email: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export default meta
type Story = StoryObj<typeof TextInput>

export const Default: Story = {
  args: {
    name: 'email',
    label: 'Email',
    isLabelHidden: true,
  },
}

export const ReadOnly: Story = {
  args: {
    ...Default.args,
    readOnly: true,
    value: 'A text wrapped in a span',
  },
}

export const WithExternalError: Story = {
  args: {
    ...Default.args,
    externalError: 'This field is required',
  },
}

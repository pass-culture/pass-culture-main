import type { Meta, StoryObj } from '@storybook/react'

import { TextInput } from './TextInput'

const meta: Meta<typeof TextInput> = {
  title: 'ui-kit/formsV2/TextInput',
  component: TextInput,
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
    error: 'This field is required',
  },
}

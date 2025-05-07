import type { Meta, StoryObj } from '@storybook/react'

import { Button } from 'ui-kit/Button/Button'

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
    isLabelHidden: false,
  },
}

export const ReadOnly: Story = {
  args: {
    ...Default.args,
    readOnly: true,
    description: 'this is email',
    value: 'A text wrapped in a span',
  },
}

export const withLabelHidden: Story = {
  args: {
    name: 'email',
    label: 'Email',
    description: 'this is email',
    isLabelHidden: true,
  },
}

export const WithExternalError: Story = {
  args: {
    ...Default.args,
    error: 'This field is required',
  },
}

export const WithInputExtension: Story = {
  args: {
    ...Default.args,
    InputExtension: <Button type="submit">Inviter</Button>,
  },
}

export const WithInputCount: Story = {
  args: {
    ...Default.args,
    count: 100,
  },
}

export const WithAll: Story = {
  args: {
    ...Default.args,
    label: 'Email',
    description: 'this is email',
    InputExtension: <Button type="submit">Inviter</Button>,
    count: 100,
    error: 'This field is required',
    required: true,
  },
}

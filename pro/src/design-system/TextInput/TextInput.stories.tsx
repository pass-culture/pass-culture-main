import type { Meta, StoryObj } from '@storybook/react'

import { TextInput } from './TextInput'

const meta: Meta<typeof TextInput> = {
  title: '@/design-system/TextInput',
  component: TextInput,
}

export default meta
type Story = StoryObj<typeof TextInput>

export const Default: Story = {
  args: {
    label: 'Default',
  },
}

export const HasDescription: Story = {
  args: {
    label: 'Label',
    description: 'description',
  },
}

export const IsDisabled: Story = {
  args: {
    label: 'Disabled',
    disabled: true,
  },
}

export const HasError: Story = {
  args: {
    label: 'Disabled',
    error: 'This is an error message',
  },
}

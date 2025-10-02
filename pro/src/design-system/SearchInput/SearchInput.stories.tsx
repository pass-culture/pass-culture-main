import type { Meta, StoryObj } from '@storybook/react-vite'

import { SearchInput } from './SearchInput'

const meta: Meta<typeof SearchInput> = {
  title: '@/design-system/SearchInput',
  component: SearchInput,
}

export default meta
type Story = StoryObj<typeof SearchInput>

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
    value: 'test'
  },
}

export const HasError: Story = {
  args: {
    label: 'Disabled',
    error: 'This is an error message',
  },
}

export const IsRequired: Story = {
  args: {
    label: 'Required',
    required: true,
  },
}

export const HasCharactersCount: Story = {
  args: {
    label: 'Characters count',
    maxCharactersCount: 200
  },
}

export const HasCharactersCountAndError: Story = {
  args: {
    label: 'Characters count and error',
    maxCharactersCount: 200,
    error: 'This is an error message',
  },
}

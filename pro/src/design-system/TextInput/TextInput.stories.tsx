import type { Meta, StoryObj } from '@storybook/react'
import fullClearIcon from 'icons/full-clear.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'

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

export const IsRequired: Story = {
  args: {
    label: 'Required',
    required: true,
  },
}

export const HasCharactersCount: Story = {
  args: {
    label: 'Characters count',
    charactersCount: { current: 100, max: 200 },
  },
}

export const HasCharactersCountAndError: Story = {
  args: {
    label: 'Characters count and error',
    charactersCount: { current: 100, max: 200 },
    error: 'This is an error message',
  },
}

export const HasIcon: Story = {
  args: {
    label: 'Icon',
    icon: strokeSearchIcon,
  },
}

export const HasIconButton: Story = {
  args: {
    label: 'Button',
    iconButton: {
      icon: fullClearIcon,
      label: 'Label du bouton',
      onClick: () => {},
    },
  },
}

export const WithEverything: Story = {
  args: {
    label: 'With everything',
    description: 'Format: test@test.co',
    error: 'This is an error message',
    charactersCount: { current: 100, max: 200 },
    icon: strokeSearchIcon,
    iconButton: {
      icon: fullClearIcon,
      label: 'Label du bouton',
      onClick: () => {},
    },
  },
}

export const WithExtension: Story = {
  args: {
    label: 'With extension',
    description: 'Format: test@test.co',
    error: 'This is an error message',
    charactersCount: { current: 100, max: 200 },
    extension: <>Extension</>,
  },
}

import type { Meta, StoryObj } from '@storybook/react-vite'

import { PasswordInput } from './PasswordInput'
import { ChangeEvent, useState } from 'react'

const meta: Meta<typeof PasswordInput> = {
  title: '@/design-system/PasswordInput',
  component: PasswordInput,
}


export default meta
type Story = StoryObj<typeof PasswordInput>

export const Default: Story = {
  args: {
    label: 'Default',
    value: ','
  },
}

export const Interactive: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return (
      <PasswordInput
        {...args}
        value={value}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value)}
      />
    )
  },
  args: {
    label: 'Mot de passe interactif',
    name: 'password',
    displayValidation: true
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
    value: 'coucou',
    onChange: () => {}
  },
}

export const HasError: Story = {
  args: {
    label: 'Disabled',
    error: 'This is an error message',
  },
}

export const IsRequiredSymbol: Story = {
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'symbol'
  },
}

export const IsRequiredExplicit: Story = {
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'explicit'
  },
}


export const WithEverything: Story = {
  args: {
    label: 'With everything',
    description: 'Format: test@test.co',
    error: 'This is an error message',
    required: true,
    requiredIndicator: 'explicit',
    displayValidation: true
  },
}

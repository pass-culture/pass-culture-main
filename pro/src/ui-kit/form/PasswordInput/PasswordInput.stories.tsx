import type { Meta, StoryObj } from '@storybook/react'

import { PasswordInput } from './PasswordInput'

const meta: Meta<typeof PasswordInput> = {
  title: '@/ui-kit/formsV2/PasswordInput',
  component: PasswordInput,
}

export default meta
type Story = StoryObj<typeof PasswordInput>

export const Default: Story = {
  args: {
    name: 'password',
    label: 'Mot de passe *',
  },
}

export const WithRequiredError: Story = {
  args: {
    ...Default.args,
    error: 'Ce champs est requis',
  },
}

export const WithDescription: Story = {
  args: {
    ...Default.args,
    description: 'Choisissez un mot de passe fort et difficile à deviner',
  },
}

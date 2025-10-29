import type { StoryObj } from '@storybook/react-vite'

import { FieldLayout } from './FieldLayout'

export default {
  title: '@/ui-kit/forms/shared/FieldLayout',
  component: FieldLayout,
}

export const Default: StoryObj<typeof FieldLayout> = {
  args: {
    label: 'Votre numéro de téléphone',
    name: 'string',
    className: 'string',
    showError: true,
    error: 'error message',
    count: 10,
    maxLength: 100,
    required: false,
    children: <input type="text" />,
  },
}

import type { StoryObj } from '@storybook/react'

import { BaseFileInput } from './BaseFileInput'

export default {
  title: '@/ui-kit/forms/shared/FileInput',
  component: BaseFileInput,
}

export const Default: StoryObj<typeof BaseFileInput> = {
  args: {
    label: 'Importer une image depuis l’ordinateur',
    isValid: true,
    fileTypes: ['image/jpeg', 'image/png'],
    onChange: alert,
  },
}

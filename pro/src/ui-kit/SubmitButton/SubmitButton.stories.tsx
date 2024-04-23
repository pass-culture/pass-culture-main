import type { StoryObj } from '@storybook/react'

import { SubmitButton, SubmitButtonProps } from './SubmitButton'

export default {
  title: 'ui-kit/SubmitButton',
  component: SubmitButton,
}

export const Default: StoryObj<SubmitButtonProps> = {
  args: {
    children: 'Envoyer',
    isLoading: false,
    disabled: false,
  },
}

export const Loading: StoryObj<SubmitButtonProps> = {
  args: {
    children: 'Envoyer',
    isLoading: true,
    disabled: false,
  },
}

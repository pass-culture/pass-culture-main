import type { StoryObj } from '@storybook/react'

import BaseRadio from './BaseRadio'
import { BaseRadioVariant } from './types'

export default {
  title: 'ui-kit/forms/shared/BaseRadio',
  component: BaseRadio,
}

export const Default: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: false,
    variant: BaseRadioVariant.PRIMARY,
  },
}

export const WithBorder: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: false,
    withBorder: true,
    variant: BaseRadioVariant.PRIMARY,
  },
}

import type { StoryObj } from '@storybook/react'

import { BaseRadio, RadioVariant } from './BaseRadio'

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
  },
}

export const WithBorder: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: false,
    variant: RadioVariant.BOX,
  },
}

export const WithChildren: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    childrenOnChecked: (
      <div>Sub content displayed when the radio input is selected.</div>
    ),
  },
}

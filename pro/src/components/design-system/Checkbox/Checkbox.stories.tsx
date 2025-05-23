import type { StoryObj } from '@storybook/react'

import dogo from '../../../../cypress/data/dog.jpg'

import { Checkbox } from './Checkbox'

export default {
  title: 'design-system/Checkbox',
  component: Checkbox,
}

export const Default: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    checked: false,
    disabled: true,
    hasError: true,
    description: 'Description ou exemple pour préciser',
    asset: {
      variant: 'image',
      src: dogo,
      size: 'S',
    },
    display: 'fit',
  },
}

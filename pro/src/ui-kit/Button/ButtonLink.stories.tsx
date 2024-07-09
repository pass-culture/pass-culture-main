/* istanbul ignore file */
import type { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-react-router-v6'

import fullBackIcon from 'icons/full-back.svg'
import fullEditIcon from 'icons/full-edit.svg'

import { ButtonLink } from './ButtonLink'
import { ButtonVariant } from './types'

export default {
  title: 'ui-kit/ButtonLink',
  component: ButtonLink,
  decorators: [withRouter],
  argTypes: {
    variant: {
      options: ['primary', 'secondary', 'ternary', 'quaternary', 'box'],
      control: 'radio',
    },
    iconPosition: {
      options: ['left', 'right'],
      control: 'radio',
    },
  },
}

export const Ternary: StoryObj<typeof ButtonLink> = {
  args: {
    children: 'Éditer',
    variant: ButtonVariant.TERNARY,
    to: '/my-path',
    isExternal: false,
  },
}

export const TernaryWithIcon: StoryObj<typeof ButtonLink> = {
  args: {
    ...Ternary.args,
    icon: fullEditIcon,
  },
}

export const TernaryPinkWithIcon: StoryObj<typeof ButtonLink> = {
  args: {
    ...TernaryWithIcon.args,
    variant: ButtonVariant.TERNARYPINK,
  },
}

export const QuaternaryWithIcon: StoryObj<typeof ButtonLink> = {
  args: {
    children: 'Accueil',
    variant: ButtonVariant.QUATERNARY,
    icon: fullBackIcon,
    to: '/my-path',
    isExternal: false,
  },
}

export const QuaternaryPinkWithIcon: StoryObj<typeof ButtonLink> = {
  args: {
    ...QuaternaryWithIcon.args,
    variant: ButtonVariant.QUATERNARYPINK,
  },
}

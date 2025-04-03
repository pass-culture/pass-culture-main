import type { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import fullEditIcon from 'icons/full-edit.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'

import { Button } from './Button'
import { ButtonVariant, IconPositionEnum } from './types'

export default {
  title: 'ui-kit/Button',
  decorators: [
    withRouter,
    (Story: any) => (
      <div style={{ margin: '50px', display: 'flex' }}>
        <Story />
      </div>
    ),
  ],
  argTypes: {
    variant: {
      options: [
        'primary',
        'secondary',
        'ternary',
        'quaternary',
        'ternary-brand',
        'box',
      ],
      control: 'radio',
    },
    iconPosition: {
      options: ['left', 'right'],
      control: 'radio',
    },
    isLoading: {
      options: [true, false],
      control: 'radio',
    },
  },
  component: Button,
}

export const DefaultButton: StoryObj<typeof Button> = {
  args: {
    children: 'Hello world',
    disabled: false,
    variant: ButtonVariant.PRIMARY,
    iconPosition: IconPositionEnum.LEFT,
  },
}

export const DefaultButtonWithIcon: StoryObj<typeof Button> = {
  args: {
    ...DefaultButton.args,
    icon: fullLinkIcon,
  },
}

export const DefaultSecondaryButton: StoryObj<typeof Button> = {
  args: {
    children: 'Hello world',
    disabled: false,
    variant: ButtonVariant.SECONDARY,
  },
}

export const WithTooltip: StoryObj<typeof Button> = {
  args: {
    ...DefaultButton.args,
    tooltipContent: (
      <>Créer une offre réservable pour un établissement scolaire</>
    ),
    icon: fullEditIcon,
    iconPosition: IconPositionEnum.CENTER,
    variant: ButtonVariant.SECONDARY,
    children: null,
  },
}

export const BoxButtonWithIcon: StoryObj<typeof Button> = {
  args: {
    children: 'Hello world',
    disabled: false,
    variant: ButtonVariant.BOX,
    iconPosition: IconPositionEnum.LEFT,
    icon: fullNextIcon,
  },
}

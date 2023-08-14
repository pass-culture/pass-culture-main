/* istanbul ignore file */
import type { Story } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import fullEditIcon from 'icons/full-edit.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'

import { ButtonProps } from './Button'
import { ButtonVariant, IconPositionEnum } from './types'

import { Button } from './index'

export default {
  title: 'ui-kit/Button',
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
    isLoading: {
      options: [true, false],
      control: 'radio',
    },
    hasTooltip: {
      options: [true, false],
      control: 'radio',
    },
  },
}

const Template: Story<ButtonProps> = args => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <Button {...args}>{args.children}</Button>
  </div>
)

export const DefaultButton = Template.bind({})

DefaultButton.args = {
  children: 'Hello world',
  disabled: false,
  variant: ButtonVariant.PRIMARY,
  iconPosition: IconPositionEnum.LEFT,
}

export const DefaultButtonWithIcon = Template.bind({})

DefaultButtonWithIcon.args = {
  ...DefaultButton.args,
  icon: fullLinkIcon,
}

export const DefaultSecondaryButton = Template.bind({})

DefaultSecondaryButton.args = {
  children: 'Hello world',
  disabled: false,
  variant: ButtonVariant.SECONDARY,
}

export const WithTooltip = Template.bind({})

WithTooltip.args = {
  ...DefaultButton.args,
  children: 'Créer une offre réservable pour un établissement scolaire',
  icon: fullEditIcon,
  iconPosition: IconPositionEnum.CENTER,
  variant: ButtonVariant.SECONDARY,
  hasTooltip: true,
}

export const BoxButtonWithIcon = Template.bind({})
BoxButtonWithIcon.args = {
  children: 'Hello world',
  disabled: false,
  variant: ButtonVariant.BOX,
  iconPosition: IconPositionEnum.LEFT,
  icon: fullNextIcon,
}

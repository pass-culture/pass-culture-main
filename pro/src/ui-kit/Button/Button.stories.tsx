/* istanbul ignore file */
import type { Story } from '@storybook/react'
import React from 'react'

import fullBackIcon from 'icons/full-back.svg'
import fullEditIcon from 'icons/full-edit.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'

import { withRouterDecorator } from '../../stories/decorators/withRouter'

import { ButtonProps } from './Button'
import { ButtonLinkProps } from './ButtonLink'
import { ButtonVariant, IconPositionEnum } from './types'

import { Button, ButtonLink } from './index'

export default {
  title: 'ui-kit/Button',
  decorators: [withRouterDecorator],
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

const Template: Story<ButtonProps> = args => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <Button {...args}>{args.children}</Button>
  </div>
)

const TemplateLink: Story<ButtonLinkProps> = args => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <ButtonLink {...args}>{args.children}</ButtonLink>
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

export const LinkButton = TemplateLink.bind({})

LinkButton.args = {
  children: 'Éditer',
  variant: ButtonVariant.TERNARY,
  link: { to: '/my-path', isExternal: false },
}

export const LinkButtonWithIcon = TemplateLink.bind({})

LinkButtonWithIcon.args = {
  ...LinkButton.args,
  icon: fullEditIcon,
}

export const LinkQuaternaryButtonWithIcon = TemplateLink.bind({})

LinkQuaternaryButtonWithIcon.args = {
  children: 'Accueil',
  variant: ButtonVariant.QUATERNARY,
  icon: fullBackIcon,
  link: { to: '/my-path', isExternal: false },
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

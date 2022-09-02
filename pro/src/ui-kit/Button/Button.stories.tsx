import type { Story } from '@storybook/react'
import React from 'react'

import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'

import { withRouterDecorator } from '../../stories/decorators/withRouter'

import { ButtonVariant, SharedButtonProps } from './types'

import { Button, ButtonLink } from './index'

export default {
  title: 'ui-kit/Button',
  decorators: [withRouterDecorator],
  argTypes: {
    variant: {
      options: ['primary', 'secondary', 'ternary'],
      control: 'radio',
    },
  },
}

const Template: Story<{
  children: string
  disabled: boolean
  variant: ButtonVariant
  Icon?: SharedButtonProps['Icon']
}> = args => <Button {...args}>{args.children}</Button>

const TemplateLink: Story<{
  children: string
  variant: ButtonVariant
  link: {
    to: string
    isExternal: boolean
  }
  Icon?: SharedButtonProps['Icon']
  isDisabled: boolean
}> = args => <ButtonLink {...args}>{args.children}</ButtonLink>

export const DefaultButton = Template.bind({})

DefaultButton.args = {
  children: 'Hello world',
  disabled: false,
  variant: ButtonVariant.PRIMARY,
}

export const DefaultButtonWithIcon = Template.bind({})

DefaultButtonWithIcon.args = {
  ...DefaultButton.args,
  Icon: LinkIcon,
}

export const DefaultSecondaryButton = Template.bind({})

DefaultSecondaryButton.args = {
  children: 'Hello world',
  disabled: false,
  variant: ButtonVariant.SECONDARY,
}

export const LinkButton = TemplateLink.bind({})

LinkButton.args = {
  children: 'Hello world',
  isDisabled: false,
  variant: ButtonLink.variant.TERNARY,
  link: { to: '/my-path', isExternal: false },
}

export const LinkButtonWithIcon = TemplateLink.bind({})

LinkButtonWithIcon.args = {
  ...LinkButton.args,
  Icon: PenIcon,
}

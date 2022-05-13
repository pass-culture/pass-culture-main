import { Button, ButtonLink } from './index'
import { ButtonVariant, SharedButtonProps } from './types'

import React from 'react'
import { Story } from '@storybook/react'
import { ReactComponent as StoryIcon } from './assets/storyIcon.svg'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

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
  to: string
  Icon?: SharedButtonProps['Icon']
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
  Icon: StoryIcon,
}

export const LinkButton = TemplateLink.bind({})

LinkButton.args = {
  children: 'Hello world',
  variant: ButtonLink.variant.TERNARY,
  to: '/my-path',
}

export const LinkButtonWithIcon = TemplateLink.bind({})

LinkButtonWithIcon.args = {
  ...LinkButton.args,
  Icon: StoryIcon,
}

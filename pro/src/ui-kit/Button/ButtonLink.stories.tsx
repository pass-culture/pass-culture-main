/* istanbul ignore file */
import type { Story } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import fullBackIcon from 'icons/full-back.svg'
import fullEditIcon from 'icons/full-edit.svg'

import { ButtonLinkProps } from './ButtonLink'
import { ButtonVariant } from './types'

import { ButtonLink } from './index'

export default {
  title: 'ui-kit/ButtonLink',
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

const TemplateLink: Story<ButtonLinkProps> = args => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <ButtonLink {...args}>{args.children}</ButtonLink>
  </div>
)

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

import type { Story } from '@storybook/react'
import React from 'react'

import UserIcon from 'icons/user.svg'

import { SvgIcon, SvgIconProps } from './SvgIcon'

export default {
  title: 'ui-kit/SvgIcon',
  component: SvgIcon,
}

const Template: Story<SvgIconProps> = args => {
  return <SvgIcon {...args} />
}

export const Default = Template.bind({})
Default.args = {
  src: UserIcon,
  alt: 'A user',
}

import type { Story } from '@storybook/react'
import React from 'react'

import strokeUserIcon from 'icons/stroke-user.svg'

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
  src: strokeUserIcon,
  alt: 'A user',
}

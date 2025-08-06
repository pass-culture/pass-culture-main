import type { StoryObj } from '@storybook/react'

import strokeUserIcon from '@/icons/stroke-user.svg'

import { SvgIcon, SvgIconProps } from './SvgIcon'

export default {
  title: '@/ui-kit/SvgIcon',
  component: SvgIcon,
}

export const Default: StoryObj<SvgIconProps> = {
  args: {
    src: strokeUserIcon,
    alt: 'A user',
    width: '50',
  },
}

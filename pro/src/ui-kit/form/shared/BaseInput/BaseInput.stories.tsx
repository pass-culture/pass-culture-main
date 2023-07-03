import type { Story } from '@storybook/react'
import React from 'react'

import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import BaseInput from './BaseInput'

export default {
  title: 'ui-kit/forms/shared/BaseInput',
  component: BaseInput,
}

const Template: Story<{
  hasError: boolean
  RightIcon: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}> = args => (
  <div>
    <BaseInput {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  hasError: false,
  RightIcon: () => <SvgIcon alt="" src={strokeCalendarIcon} />,
}

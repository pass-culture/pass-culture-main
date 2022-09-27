import type { Story } from '@storybook/react'
import React from 'react'

import Tag from 'ui-kit/Tag'

import TooltipWrapper, { ITooltipWrapperProps } from './TooltipWrapper'

export default {
  title: 'ui-kit/TooltipWrapper',
  component: TooltipWrapper,
}

const Template: Story<ITooltipWrapperProps> = props => (
  <div style={{ margin: '30px', display: 'flex' }}>
    <TooltipWrapper {...props}>
      <Tag label={'Hover me'} />
    </TooltipWrapper>
  </div>
)

export const Default = Template.bind({})
Default.args = {
  title: 'Mon super tooltip',
}

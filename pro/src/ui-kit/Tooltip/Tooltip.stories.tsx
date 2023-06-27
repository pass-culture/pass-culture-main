import type { Story } from '@storybook/react'
import React from 'react'

import Tooltip, { TooltipProps } from './Tooltip'

export default {
  title: 'ui-kit/Tooltip',
  component: Tooltip,
}

const Template: Story<TooltipProps> = ({ content, children }) => {
  return (
    <div style={{ padding: '4rem' }}>
      <Tooltip id="someid" content={content}>
        {children}
      </Tooltip>
    </div>
  )
}

export const Default = Template.bind({})

Default.args = {
  content: 'Contenu du tooltip',
  children: 'Hover me!',
}

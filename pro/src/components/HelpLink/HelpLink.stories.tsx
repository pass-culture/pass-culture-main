import React from 'react'

import { HelpLink } from './HelpLink'

export default {
  title: 'components/HelpLink',
  component: HelpLink,
  decorators: [
    (Story: any) => (
      <div style={{ width: 500, height: 500 }}>
        <Story />
      </div>
    ),
  ],
}

export const Default = {}

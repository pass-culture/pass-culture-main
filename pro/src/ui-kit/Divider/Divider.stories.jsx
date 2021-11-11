/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import React from 'react'

import Divider from './Divider'

export default {
  title: 'ui-kit/Divider',
  component: Divider,
}

const Template = args => (
  <div>
    <p>
      First text
    </p>
    <Divider {...args} />
    <p>
      Second text
    </p>
  </div>
)

export const Default = Template.bind({})

Default.args = {
  size: 'medium',
}

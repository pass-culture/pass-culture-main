import React from 'react'

import Tag from './Tag'

export default {
  title: 'ui-kit/Tag',
  component: Tag,
}

const Template = args => (
  <Tag {...args}>
    {args.children}
  </Tag>
)

export const Default = Template.bind({})

Default.args = {
  children: 'Offre collective',
}

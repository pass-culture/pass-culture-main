import React from 'react'

import Card from './Card'

export default {
  title: 'ui-kit/Card',
  component: Card,
}

const Template = args => (
  <div>
    <Card {...args}>{args.children}</Card>
  </div>
)

export const Default = Template.bind({})

Default.args = {
  children: 'Card content',
  titleIcon: 'ico-play',
  title: 'Card title',
  secondaryTitle: 'Card secondary title',
}

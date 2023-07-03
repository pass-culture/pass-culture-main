import type { Story } from '@storybook/react'
import React from 'react'

import fullTrashIcon from 'icons/full-trash.svg'

import ListIconButton, { ListIconButtonProps } from './ListIconButton'

export default {
  title: 'ui-kit/ListIconButton',
  component: ListIconButton,
}

const Template: Story<ListIconButtonProps> = props => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <ListIconButton {...props}>{props.children}</ListIconButton>
  </div>
)

export const Default = Template.bind({})

Default.args = {
  icon: fullTrashIcon,
  children: 'Duplicate',
  hasTooltip: true,
}

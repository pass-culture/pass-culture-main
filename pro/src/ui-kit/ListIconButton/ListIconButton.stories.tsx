import type { Story } from '@storybook/react'
import React from 'react'

import { ReactComponent as TrashIcon } from 'icons/ico-trash-filled.svg'

import ListIconButton, { IListIconButtonProps } from './ListIconButton'
export default {
  title: 'ui-kit/ListIconButton',
  component: ListIconButton,
}

const Template: Story<IListIconButtonProps> = props => (
  <div style={{ margin: '50px', display: 'flex' }}>
    <ListIconButton {...props}>{props.children}</ListIconButton>
  </div>
)

export const Default = Template.bind({})

Default.args = {
  Icon: TrashIcon,
  children: 'Duplicate',
  hasTooltip: true,
}

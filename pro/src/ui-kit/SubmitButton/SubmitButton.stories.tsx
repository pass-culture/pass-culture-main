import type { Story } from '@storybook/react'
import React from 'react'

import SubmitButton, { ISubmitButtonProps } from './SubmitButton'

export default {
  title: 'ui-kit/SubmitButton',
  component: SubmitButton,
}

const Template: Story<ISubmitButtonProps> = props => (
  <div style={{ maxWidth: '316px' }}>
    <SubmitButton {...props} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  children: 'Envoyer',
  isLoading: false,
  disabled: false,
}

export const Loading = Template.bind({})

Loading.args = {
  children: 'Envoyer',
  isLoading: true,
  disabled: false,
}

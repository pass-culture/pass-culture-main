import { ComponentStory } from '@storybook/react'
import React from 'react'

import Notification from './Notification'

export default {
  title: 'ui-kit/Notification',
}

const Template: ComponentStory<typeof Notification> = args => (
  <Notification {...args} />
)

export const Error = Template.bind({})
Error.args = {
  notification: {
    text: 'Une erreur fatale est survenue',
    type: 'error',
  },
}

export const Success = Template.bind({})
Success.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte',
    type: 'success',
  },
}

export const Pending = Template.bind({})
Pending.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
    type: 'pending',
  },
}

export const Information = Template.bind({})
Information.args = {
  notification: {
    text: 'Ceci est une information',
    type: 'information',
  },
}

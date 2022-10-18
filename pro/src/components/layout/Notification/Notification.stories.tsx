import type { ComponentStory } from '@storybook/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import Notification from './Notification'

export default {
  title: 'ui-kit/Notification',
}

const Template: ComponentStory<typeof Notification> = store => (
  <Provider store={configureTestStore(store)}>
    <Notification />
  </Provider>
)

export const Error = Template.bind({})
Error.args = {
  notification: {
    text: 'Une erreur fatale est survenue',
    type: 'error',
    duration: 2000,
  },
}

export const Success = Template.bind({})
Success.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte',
    type: 'success',
    duration: 2000,
  },
}

export const Pending = Template.bind({})
Pending.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
    type: 'pending',
    duration: 2000,
  },
}

export const Information = Template.bind({})
Information.args = {
  notification: {
    text: 'Ceci est une information',
    type: 'information',
    duration: 2000,
  },
}

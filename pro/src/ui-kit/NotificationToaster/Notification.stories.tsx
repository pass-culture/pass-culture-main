import type { Story } from '@storybook/react'
import React from 'react'

import { NotificationTypeEnum } from 'hooks/useNotification'

import NotificationToaster, {
  NotificationToasterProps,
} from './NotificationToaster'

export default {
  title: 'ui-kit/Notification',
  component: NotificationToaster,
}

const Template: Story<NotificationToasterProps> = props => (
  <NotificationToaster {...props} />
)

export const Error = Template.bind({})
Error.args = {
  notification: {
    text: 'Une erreur fatale est survenue',
    type: NotificationTypeEnum.ERROR,
    duration: 2000,
  },
  isVisible: true,
  isStickyBarOpen: false,
}

export const Success = Template.bind({})
Success.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte',
    type: NotificationTypeEnum.SUCCESS,
    duration: 2000,
  },
  isVisible: true,
  isStickyBarOpen: false,
}

export const Pending = Template.bind({})
Pending.args = {
  notification: {
    text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
    type: NotificationTypeEnum.PENDING,
    duration: 2000,
  },
  isVisible: true,
  isStickyBarOpen: false,
}

export const Information = Template.bind({})
Information.args = {
  notification: {
    text: 'Ceci est une information',
    type: NotificationTypeEnum.INFORMATION,
    duration: 2000,
  },
  isVisible: true,
  isStickyBarOpen: false,
}

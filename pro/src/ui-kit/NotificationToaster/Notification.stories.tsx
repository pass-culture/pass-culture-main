import type { StoryObj } from '@storybook/react'

import { NotificationTypeEnum } from 'commons/hooks/useNotification'

import { NotificationToaster } from './NotificationToaster'

export default {
  title: 'ui-kit/Notification',
  component: NotificationToaster,
}

export const Error: StoryObj<typeof NotificationToaster> = {
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000,
    },
    isVisible: true,
    isStickyBarOpen: false,
  },
}

export const Success: StoryObj<typeof NotificationToaster> = {
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000,
    },
    isVisible: true,
    isStickyBarOpen: false,
  },
}

export const Information: StoryObj<typeof NotificationToaster> = {
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000,
    },
    isVisible: true,
    isStickyBarOpen: false,
  },
}

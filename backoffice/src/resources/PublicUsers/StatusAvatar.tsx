import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import { Avatar } from '@mui/material'
import { green, red, yellow } from '@mui/material/colors'
import React from 'react'

import { CheckHistory, SubscriptionItem, SubscriptionItemStatus } from './types'

type Props = {
  subscriptionItem: SubscriptionItem | CheckHistory | undefined
}

export const StatusAvatar = ({ subscriptionItem }: Props) => {
  let color, icon

  switch (subscriptionItem?.status) {
    case SubscriptionItemStatus.OK:
      color = green['700']
      icon = <CheckCircleOutlineIcon />
      break
    case SubscriptionItemStatus.KO:
      color = red['700']
      icon = <ErrorOutlineIcon />
      break
    default:
      color = yellow['700']
      icon = <ErrorOutlineIcon />
  }

  return <Avatar sx={{ bgcolor: color }}>{icon}</Avatar>
}

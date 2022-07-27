import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import { Avatar, Tooltip } from '@mui/material'
import { green, red, yellow } from '@mui/material/colors'
import React from 'react'

import { FraudCheck, SubscriptionItem, SubscriptionItemStatus } from '../types'

type Props = {
  item: SubscriptionItem | FraudCheck | undefined
}

export const StatusAvatar = ({ item }: Props) => {
  let color, icon
  icon = <ErrorOutlineIcon />
  color = red['700']

  const itemLabel = item?.status?.toUpperCase()

  switch (item?.status) {
    case SubscriptionItemStatus.OK:
      color = green['700']
      icon = <CheckCircleOutlineIcon />
      break
    case SubscriptionItemStatus.KO:
      break
    default:
      color = yellow['700']
      return (
        <Tooltip
          title={itemLabel ? itemLabel : 'Statut inconnu'}
          placement="right"
        >
          <Avatar sx={{ bgcolor: color }}>{icon}</Avatar>
        </Tooltip>
      )
  }
  return <Avatar sx={{ bgcolor: color }}>{icon}</Avatar>
}

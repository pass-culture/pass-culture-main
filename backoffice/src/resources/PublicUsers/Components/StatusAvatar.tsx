import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import HighlightOffIcon from '@mui/icons-material/HighlightOff'
import { Avatar, Tooltip } from '@mui/material'
import { green, red, yellow } from '@mui/material/colors'
import React from 'react'

import {
  FraudCheckStatus,
  IdCheckItemModel,
  SubscriptionItemModel,
} from '../../../TypesFromApi'

type Props = {
  item: SubscriptionItemModel | IdCheckItemModel | undefined
}

export const StatusAvatar = ({ item }: Props) => {
  let color, icon
  icon = <ErrorOutlineIcon />
  color = red['700']

  const itemLabel = item?.status?.toUpperCase()

  switch (item?.status) {
    case FraudCheckStatus.Ok:
      color = green['700']
      icon = <CheckCircleOutlineIcon />
      break
    case FraudCheckStatus.Ko:
      break
    case FraudCheckStatus.Error:
      icon = <HighlightOffIcon />
      break
    case FraudCheckStatus.Canceled:
      icon = <DeleteForeverIcon />
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

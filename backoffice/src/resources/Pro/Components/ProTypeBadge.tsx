import { Chip } from '@mui/material'

import { ProResourceAPI, ProTypeEnum, Venue } from '../types'

type Props = {
  type: ProTypeEnum
  resource: ProResourceAPI
}

export const ProTypeBadge = ({ type, resource }: Props) => {
  let label
  switch (type) {
    case ProTypeEnum.offerer:
      label = 'Structure'
      break
    case ProTypeEnum.proUser:
      label = 'Pro'
      break
    case ProTypeEnum.venue:
      if ((resource.payload as Venue).permanent == true) {
        label = 'Lieu Permanent'
      } else {
        label = 'Lieu Non-Permanent'
      }
      break
    default:
      return null
  }
  return (
    <Chip
      color={'info'}
      label={label}
      style={{
        fontSize: '0.95rem',
      }}
    />
  )
}

import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import HighlightOffIcon from '@mui/icons-material/HighlightOff'
import { Chip } from '@mui/material'

type Props = {
  active?: boolean
  feminine?: boolean
}

export const StatusBadge = ({ active, feminine }: Props) => {
  if (active) {
    return (
      <Chip
        color={'success'}
        label={feminine ? 'Active' : 'Actif'}
        icon={<CheckCircleOutlineIcon />}
        style={{
          fontSize: '0.95rem',
        }}
      />
    )
  }
  return (
    <Chip
      color={'error'}
      label={feminine ? 'Suspendue' : 'Suspendu'}
      icon={<HighlightOffIcon />}
      style={{
        fontSize: '0.95rem',
        backgroundColor: 'black',
      }}
    />
  )
}

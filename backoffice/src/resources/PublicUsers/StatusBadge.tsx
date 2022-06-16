import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import HighlightOffIcon from '@mui/icons-material/HighlightOff'
import { Chip } from '@mui/material'

type Props = {
  active?: boolean
}

export const StatusBadge = ({ active }: Props) => {
  if (active) {
    return (
      <Chip
        color={'success'}
        label={'Actif'}
        icon={<CheckCircleOutlineIcon />}
      />
    )
  }
  return <Chip color={'error'} label={'Suspendu'} icon={<HighlightOffIcon />} />
}

import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import HighlightOffIcon from '@mui/icons-material/HighlightOff'
import WarningIcon from '@mui/icons-material/Warning'

export type BankAccountStatusBadgeProps = {
  OK: number
  KO: number
}

export const BankAccountStatusBadge = (props: BankAccountStatusBadgeProps) => {
  const { OK, KO } = props
  if (OK > 0 && KO === 0) {
    return <CheckCircleOutlineIcon color={'success'} />
  } else if (OK === 0 && KO > 0) {
    return <HighlightOffIcon color={'error'} />
  } else {
    return <WarningIcon color={'warning'} />
  }
}

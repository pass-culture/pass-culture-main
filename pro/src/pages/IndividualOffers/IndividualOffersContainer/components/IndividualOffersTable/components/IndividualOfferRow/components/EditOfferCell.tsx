import penIcon from 'icons/full-edit.svg'
import styles from 'styles/components/Cells.module.scss'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

interface EditOfferCellProps {
  editionOfferLink: string
}

export const EditOfferCell = ({ editionOfferLink }: EditOfferCellProps) => {
  return (
    <ListIconButton
      url={editionOfferLink}
      className={styles['button']}
      icon={penIcon}
    >
      Modifier
    </ListIconButton>
  )
}

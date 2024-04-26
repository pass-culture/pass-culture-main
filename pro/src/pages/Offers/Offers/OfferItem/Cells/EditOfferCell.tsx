import React from 'react'

import penIcon from 'icons/full-edit.svg'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import styles from '../OfferItem.module.scss'

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

import React from 'react'

import { Offer } from 'core/Offers/types'
import penIcon from 'icons/full-edit.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

import styles from '../../OfferItem.module.scss'

const EditOfferCell = ({
  editionOfferLink,
}: {
  isOfferEditable: boolean
  editionOfferLink: string
  offer: Offer
}) => {
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

export default EditOfferCell

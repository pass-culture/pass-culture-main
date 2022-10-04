import React from 'react'

import { ReactComponent as PlusIcon } from 'icons/ico-plus.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

const DuplicateOfferCell = ({ isTemplate }: { isTemplate: boolean }) => {
  return (
    <td className={styles['duplicate-offer-column']}>
      {isTemplate ? (
        <Button variant={ButtonVariant.SECONDARY} className={styles['button']}>
          <PlusIcon className={styles['button-icon']} />
        </Button>
      ) : null}
    </td>
  )
}
export default DuplicateOfferCell

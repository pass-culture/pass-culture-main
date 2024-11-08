import strokeShoutIcon from 'icons/stroke-shout.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './UserReview.module.scss'
import { UserReviewDialog } from './UserReviewDialog/UserReviewDialog'

export const UserReview = () => {
  return (
    <>
      <div className={styles['user-review-container']}>
        <SvgIcon
          className={styles['user-review-icon']}
          src={strokeShoutIcon}
          alt=""
          width="20"
        />
        <div>
          <span className={styles['user-review-bold-text']}>
            Que pensez-vous du pass Culture Pro ?
          </span>{' '}
          Aidez-nous à l’améliorer.
        </div>
        <DialogBuilder
          trigger={
            <Button variant={ButtonVariant.SECONDARY}>Je donne mon avis</Button>
          }
        >
          <UserReviewDialog />
        </DialogBuilder>
      </div>
    </>
  )
}

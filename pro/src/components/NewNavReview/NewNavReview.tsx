import strokeShoutIcon from 'icons/stroke-shout.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NewNavReview.module.scss'
import { NewNavReviewDialog } from './NewNavReviewDialog/NewNavReviewDialog'

export const NewNavReview = () => {
  return (
    <>
      <div className={styles['new-nav-review-container']}>
        <SvgIcon
          className={styles['new-nav-review-icon']}
          src={strokeShoutIcon}
          alt=""
          width="20"
        />
        <div>
          <span className={styles['new-nav-review-bold-text']}>
            Vous êtes sur la nouvelle interface !
          </span>{' '}
          Dites-nous ce que vous en pensez pour nous aider à l’améliorer.
        </div>
        <DialogBuilder
          trigger={
            <Button variant={ButtonVariant.SECONDARY}>Je donne mon avis</Button>
          }
        >
          <NewNavReviewDialog />
        </DialogBuilder>
      </div>
    </>
  )
}

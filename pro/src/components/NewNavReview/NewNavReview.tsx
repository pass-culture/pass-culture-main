import React, { useState } from 'react'

import strokeShoutIcon from 'icons/stroke-shout.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NewNavReview.module.scss'
import NewNavReviewDialog from './NewNavReviewDialog/NewNavReviewDialog'

const NewNavReview = () => {
  const [isReviewDialogOpen, setIsReviewDialogOpen] = useState(false)
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
        <Button
          variant={ButtonVariant.SECONDARY}
          onClick={() => setIsReviewDialogOpen(true)}
        >
          Je donne mon avis
        </Button>
      </div>
      {isReviewDialogOpen && (
        <NewNavReviewDialog setIsReviewDialogOpen={setIsReviewDialogOpen} />
      )}
    </>
  )
}

export default NewNavReview

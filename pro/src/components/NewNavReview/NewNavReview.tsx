import { useTranslation } from 'react-i18next'

import strokeShoutIcon from 'icons/stroke-shout.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NewNavReview.module.scss'
import { NewNavReviewDialog } from './NewNavReviewDialog/NewNavReviewDialog'

export const NewNavReview = () => {
  const { t } = useTranslation('common')
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
            {t('new_interface_message_part_one')}
          </span>{' '}
          {t('new_interface_message_part_two')}
        </div>
        <DialogBuilder
          trigger={
            <Button variant={ButtonVariant.SECONDARY}>
              {t('give_feedback')}
            </Button>
          }
        >
          <NewNavReviewDialog />
        </DialogBuilder>
      </div>
    </>
  )
}

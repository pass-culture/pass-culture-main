import classnames from 'classnames'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullSmsIcon from '@/icons/full-sms.svg'

import styles from './SideNavLinks.module.scss'
import { UserReviewDialog } from './UserReviewDialog/UserReviewDialog'

export const FeedbackDialogTriggerNavItem = () => (
  <UserReviewDialog
    dialogTrigger={
      <div
        className={classnames(
          styles['nav-links-item'],
          styles['nav-links-help']
        )}
      >
        <Button
          color={ButtonColor.NEUTRAL}
          icon={fullSmsIcon}
          label="Donner mon avis"
          variant={ButtonVariant.TERTIARY}
        />
      </div>
    }
  />
)

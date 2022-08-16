import React from 'react'

import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './styles'

interface IUserIdentityDetailsProps {}

const UserIdentityDetails = () => (
  <>
    <div className={styles['profile-form-description']}>
      <div className={styles['profile-form-description-column']}>
        <div className={styles['profile-form-description-title']}>{title}</div>
        <div className={styles['profile-form-description-value']}>
          {subTitle}
        </div>
      </div>
      <div className={styles['profile-form-description-column']}>
        <Button
          className={styles['profile-form-edit-button']}
          variant={ButtonVariant.TERNARY}
          onClick={() => setIsFormVisible(true)}
          Icon={() => <Icon svg="ico-pen-black" />}
        >
          Modifier
        </Button>
      </div>
    </div>
    {shouldDisplayBanner && (
      <div className={styles['profile-form-description-banner']}>{banner}</div>
    )}
  </>
)

export default UserIdentityDetails

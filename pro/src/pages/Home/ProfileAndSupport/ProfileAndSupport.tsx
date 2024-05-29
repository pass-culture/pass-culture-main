import React from 'react'

import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'

import { Profile } from './Profile'
import styles from './ProfileAndSupport.module.scss'
import { Support } from './Support'

export const ProfileAndSupport = () => {
  const hasNewInterface = useIsNewInterfaceActive()
  return (
    <>
      {!hasNewInterface && <h2 className={styles['title']}>Profil et aide</h2>}

      <div className={styles['cards-row']}>
        {!hasNewInterface && <Profile />}

        <Support />
      </div>
    </>
  )
}

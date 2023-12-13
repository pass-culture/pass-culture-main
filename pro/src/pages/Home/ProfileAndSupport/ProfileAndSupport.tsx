import React from 'react'

import { Profile } from './Profile'
import styles from './ProfileAndSupport.module.scss'
import { Support } from './Support'

export const ProfileAndSupport = () => (
  <>
    <h2 className={styles['title']}>Profil et aide</h2>

    <div className={styles['cards-row']}>
      <Profile />

      <Support />
    </div>
  </>
)

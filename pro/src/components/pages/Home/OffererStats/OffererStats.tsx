import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './OffererStats.module.scss'

const OffererStats = () => {
  const offererStatsUrl = '/statistiques'
  return (
    <>
      <h2 className="h-section-title">Statistiques</h2>
      <div className={styles['offerer-stats']}>
        <p className={styles['offerer-stats-description']}>
          A venir, section statistiques
        </p>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          className={styles['offerer-stats-button']}
          link={{
            to: offererStatsUrl,
            isExternal: false,
          }}
        >
          Voir toutes les statistiques
        </ButtonLink>
      </div>
    </>
  )
}

export default OffererStats

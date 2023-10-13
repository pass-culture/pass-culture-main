import React from 'react'

import fullMoreIcon from 'icons/full-more.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  offererId: string
}

export const StatisticsDashboard = ({
  offererId,
}: StatisticsDashboardProps) => {
  return (
    <section className={styles['section']}>
      <div className={styles['header']}>
        <h2 className={styles['title']}>Présence sur le pass Culture</h2>

        <ButtonLink
          variant={ButtonVariant.PRIMARY}
          link={{
            isExternal: false,
            to: `/offre/creation?structure=${offererId}`,
          }}
          icon={fullMoreIcon}
        >
          Créer une offre
        </ButtonLink>
      </div>
    </section>
  )
}

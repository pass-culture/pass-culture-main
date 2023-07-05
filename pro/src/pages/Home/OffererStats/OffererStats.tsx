import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullShowIcon from 'icons/full-show.svg'
import shadowCalendarIcon from 'icons/shadow-calendar.svg'
import shadowEuroIcon from 'icons/shadow-euro.svg'
import shadowTropheeIcon from 'icons/shadow-trophee.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { IconLinkBox } from 'ui-kit/IconLinkBox'

import { STEP_STATS_HASH } from '../HomepageBreadcrumb'

import styles from './OffererStats.module.scss'

const OffererStats = () => {
  const offererStatsUrl = '/statistiques'

  const { logEvent } = useAnalytics()
  const location = useLocation()

  const defaultIconLinkProps = {
    iconLink: fullShowIcon,
    linkUrl: offererStatsUrl,
    linkTitle: 'Voir le tableau',
    onClick: () => {
      logEvent?.(Events.CLICKED_VIEW_OFFERER_STATS, {
        from: location.pathname,
      })
    },
  }

  return (
    <div id={STEP_STATS_HASH}>
      <h2 className="h-section-title">Statistiques</h2>
      <div className={styles['offerer-stats']}>
        <div className={styles['offerer-stats-boxes']}>
          <IconLinkBox
            title="Top de vos offres"
            iconHeader={shadowTropheeIcon}
            {...defaultIconLinkProps}
          />
          <IconLinkBox
            title="Nombre de réservations"
            iconHeader={shadowCalendarIcon}
            {...defaultIconLinkProps}
          />
          <IconLinkBox
            title="Répartition de votre chiffre d’affaires"
            iconHeader={shadowEuroIcon}
            {...defaultIconLinkProps}
          />
        </div>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          className={styles['offerer-stats-button']}
          link={{
            to: offererStatsUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent?.(Events.CLICKED_VIEW_ALL_OFFERER_STATS, {
              from: location.pathname,
            })
          }}
        >
          Voir toutes les statistiques
        </ButtonLink>
      </div>
    </div>
  )
}

export default OffererStats

import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as CalendarIcon } from 'icons/ico-calendar-v2.svg'
import { ReactComponent as EuroIcon } from 'icons/ico-euro-v2.svg'
import { ReactComponent as TropheeIcon } from 'icons/ico-trophee.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'
import { IconLinkBox } from 'ui-kit/IconLinkBox'

// import { STEP_STATS_HASH } from '../HomepageBreadcrumb'

import styles from './OffererStats.module.scss'

const OffererStats = () => {
  const offererStatsUrl = '/statistiques'

  const { logEvent } = useAnalytics()
  const location = useLocation()

  const defaultIconLinkProps = {
    IconLink: () => <Icon svg="ico-eye-open-filled-black" />,
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
            IconHeader={TropheeIcon}
            {...defaultIconLinkProps}
          />
          <IconLinkBox
            title="Nombre de réservations"
            IconHeader={CalendarIcon}
            {...defaultIconLinkProps}
          />
          <IconLinkBox
            title="Répartition de votre chiffre d’affaires"
            IconHeader={EuroIcon}
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

import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import fullHelpIcon from 'icons/full-help.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HelpLink.module.scss'

export const HelpLink = (): JSX.Element => {
  const { logEvent } = useAnalytics()

  return (
    <a
      onClick={() =>
        logEvent(Events.CLICKED_HELP_LINK, { from: location.pathname })
      }
      className={styles['help-link']}
      href="https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-"
      rel="noreferrer"
      target="_blank"
    >
      <SvgIcon src={fullHelpIcon} alt="" width="42" />
      <span className={styles['help-link-text']}>Aide</span>
    </a>
  )
}

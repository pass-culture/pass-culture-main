import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullLinkIcon from 'icons/full-link.svg'
import fullMailIcon from 'icons/full-mail.svg'
import fullParametersIcon from 'icons/full-parameters.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { initCookieConsent } from 'utils/cookieConsentModal'

import styles from './Support.module.scss'

const Support: () => JSX.Element | null = () => {
  const isCookieBannerEnabled = useActiveFeature('WIP_ENABLE_COOKIES_BANNER')

  const { logEvent } = useAnalytics()
  const location = useLocation()
  return (
    <div className="h-support h-card h-card-secondary-hover">
      <div className={styles['card-inner']}>
        <h3 className="h-card-title">Aide et support</h3>

        <div className={styles['card-content']}>
          <ul>
            <li>
              <ButtonLink
                link={{
                  to: 'https://aide.passculture.app',
                  isExternal: true,
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
                icon={fullLinkIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_HELP_CENTER, {
                    from: location.pathname,
                  })
                }
                svgAlt="Nouvelle fenêtre"
              >
                Centre d’aide
              </ButtonLink>
            </li>

            <li>
              <ButtonLink
                link={{
                  to: 'https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0',
                  isExternal: true,
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
                icon={fullLinkIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_BEST_PRACTICES_STUDIES, {
                    from: location.pathname,
                  })
                }
                svgAlt="Nouvelle fenêtre"
              >
                Bonnes pratiques et études
              </ButtonLink>
            </li>

            <li>
              <ButtonLink
                link={{
                  to: 'mailto:support-pro@passculture.app',
                  isExternal: true,
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
                icon={fullMailIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_SUPPORT, {
                    from: location.pathname,
                  })
                }
              >
                Contacter le support par mail à <br />
                support-pro@passculture.app
              </ButtonLink>
            </li>

            <li>
              <ButtonLink
                link={{
                  to: 'https://pass.culture.fr/cgu-professionnels/',
                  isExternal: true,
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
                icon={fullLinkIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_CGU, {
                    from: location.pathname,
                  })
                }
                svgAlt="Nouvelle fenêtre"
              >
                Conditions Générales d’Utilisation
              </ButtonLink>
            </li>
            {isCookieBannerEnabled && (
              <li>
                <Button
                  variant={ButtonVariant.TERNARY}
                  icon={fullParametersIcon}
                  onClick={() => {
                    /* istanbul ignore next : library should be tested */
                    initCookieConsent().show()
                  }}
                >
                  Gestion des cookies
                </Button>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Support

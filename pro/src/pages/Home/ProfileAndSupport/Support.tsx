import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { orejime } from 'app/App/analytics/orejime'
import { Events } from 'core/FirebaseEvents/constants'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullLinkIcon from 'icons/full-link.svg'
import fullMailIcon from 'icons/full-mail.svg'
import fullParametersIcon from 'icons/full-parameters.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Card } from '../Card'

import styles from './Support.module.scss'

export const Support: () => JSX.Element | null = () => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  return (
    <Card>
      <h3 className={styles['title']}>Aide et support</h3>

      <div className={styles['card-content']}>
        <ul>
          <li>
            <ButtonLink
              to="https://aide.passculture.app"
              isExternal
              opensInNewTab
              icon={fullLinkIcon}
              onClick={() =>
                logEvent(Events.CLICKED_HELP_CENTER, {
                  from: location.pathname,
                })
              }
            >
              Centre d’aide
            </ButtonLink>
          </li>

          <li>
            <ButtonLink
              to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
              isExternal
              opensInNewTab
              icon={fullLinkIcon}
              onClick={() =>
                logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
                  from: location.pathname,
                })
              }
            >
              Bonnes pratiques et études
            </ButtonLink>
          </li>

          <li>
            <ButtonLink
              to="mailto:support-pro@passculture.app"
              isExternal
              opensInNewTab
              icon={fullMailIcon}
              onClick={() =>
                logEvent(Events.CLICKED_CONSULT_SUPPORT, {
                  from: location.pathname,
                })
              }
            >
              Contacter le support par mail à <br />
              support-pro@passculture.app
            </ButtonLink>
          </li>
          {!isNewSideBarNavigation && (
            <>
              <li>
                <ButtonLink
                  to="https://pass.culture.fr/cgu-professionnels/"
                  isExternal
                  opensInNewTab
                  icon={fullLinkIcon}
                  onClick={() =>
                    logEvent(Events.CLICKED_CONSULT_CGU, {
                      from: location.pathname,
                    })
                  }
                >
                  Conditions Générales d’Utilisation
                </ButtonLink>
              </li>
              <li>
                <Button
                  variant={ButtonVariant.TERNARY}
                  icon={fullParametersIcon}
                  onClick={() => {
                    /* istanbul ignore next : library should be tested */
                    orejime.show()
                  }}
                >
                  Gestion des cookies
                </Button>
              </li>
            </>
          )}
        </ul>
      </div>
    </Card>
  )
}

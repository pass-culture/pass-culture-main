import React from 'react'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { ReactComponent as MailIcon } from 'icons/ico-mail.svg'
import { ButtonLink } from 'ui-kit'

const Support = () => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  return (
    <div className="h-support h-card h-card-secondary-hover">
      <div className="h-card-inner">
        <h3 className="h-card-title">Aide et support</h3>

        <div className="h-card-content">
          <ul className="hs-link-list">
            <li>
              <ButtonLink
                link={{
                  to: 'https://aide.passculture.app',
                  isExternal: true,
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
                Icon={LinkIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_HELP_CENTER, {
                    from: location.pathname,
                  })
                }
              >
                Centre d’aide
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
                Icon={MailIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_SUPPORT, {
                    from: location.pathname,
                  })
                }
              >
                Contacter le support
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
                Icon={LinkIcon}
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_CGU, {
                    from: location.pathname,
                  })
                }
              >
                Conditions Générales d’Utilisation
              </ButtonLink>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Support

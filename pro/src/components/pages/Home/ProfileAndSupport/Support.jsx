import React from 'react'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import Icon from 'components/layout/Icon'
import { Events } from 'core/FirebaseEvents/constants'

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
              <a
                className="hs-link tertiary-link"
                href="https://aide.passculture.app"
                onClick={() =>
                  logEvent?.(Events.CLICKED_HELP_CENTER, {
                    from: location.pathname,
                  })
                }
                rel="noopener noreferrer"
                target="_blank"
              >
                <div className="ico-container">
                  <Icon svg="ico-external-site" />
                </div>
                Centre d’aide
              </a>
            </li>

            <li>
              <a
                className="hs-link tertiary-link"
                href="mailto:support-pro@passculture.app"
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_SUPPORT, {
                    from: location.pathname,
                  })
                }
                rel="noopener noreferrer"
                target="_blank"
              >
                <div className="ico-container">
                  <Icon className="ico-mail" svg="ico-mail" />
                </div>
                Contacter le support
              </a>
            </li>

            <li>
              <a
                className="hs-link tertiary-link"
                href="https://pass.culture.fr/cgu-professionnels/"
                onClick={() =>
                  logEvent?.(Events.CLICKED_CONSULT_CGU, {
                    from: location.pathname,
                  })
                }
                rel="noopener noreferrer"
                target="_blank"
              >
                <div className="ico-container">
                  <Icon svg="ico-external-site" />
                </div>
                Conditions Générales d’Utilisation
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Support

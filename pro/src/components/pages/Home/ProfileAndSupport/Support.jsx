import React from 'react'

import Icon from 'components/layout/Icon'

const Support = () => {
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

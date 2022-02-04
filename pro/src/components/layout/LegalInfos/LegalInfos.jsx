import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon'

export const LegalInfos = ({ title, className }) => (
  <div className={`legal-infos ${className}`}>
    <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
    <a
      className="quaternary-link"
      href="https://pass.culture.fr/cgu-professionnels/"
      rel="noopener noreferrer"
      target="_blank"
    >
      <Icon svg="ico-external-site-red" />
      <span>Conditions Générales d’Utilisation</span>
    </a>
    <span>{' ainsi que notre '}</span>
    <a
      className="quaternary-link"
      href="https://pass.culture.fr/donnees-personnelles/"
      rel="noopener noreferrer"
      target="_blank"
    >
      <Icon svg="ico-external-site-red" />
      <span>Charte des Données Personnelles</span>
    </a>
    <span>
      {
        '. Pour en savoir plus sur la gestion de vos données personnelles et pour exercer vos droits, ou répondre à toute autre question, '
      }
    </span>
    <a
      className="quaternary-link"
      href="mailto:support-pro@passculture.app"
      rel="noopener noreferrer"
      target="_blank"
    >
      <Icon svg="ico-email-red" />
      <span>contactez notre support.</span>
    </a>
  </div>
)

LegalInfos.propTypes = {
  className: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

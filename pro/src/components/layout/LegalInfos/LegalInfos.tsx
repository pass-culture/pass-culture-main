import React from 'react'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'

import Icon from '../Icon'

interface ILegalInfo {
  title: string
  className: string
}

export const LegalInfos = ({ title, className }: ILegalInfo): JSX.Element => {
  const location = useLocation()
  const analytics = useAnalytics()
  return (
    <div className={`legal-infos ${className}`}>
      <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
      <a
        className="quaternary-link"
        href="https://pass.culture.fr/cgu-professionnels/"
        onClick={() => analytics.logConsultCGUClick(location.pathname)}
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
        onClick={() => analytics.logPersonalDataClick(location.pathname)}
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
        onClick={() => analytics.logConsultSupportClick(location.pathname)}
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-email-red" />
        <span>contactez notre support.</span>
      </a>
    </div>
  )
}

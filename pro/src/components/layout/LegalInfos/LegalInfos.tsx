import React from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { Events } from 'core/FirebaseEvents/constants'
import { RootState } from 'store/reducers'

interface ILegalInfoProps {
  title: string
  className: string
}

const LegalInfos = ({ title, className }: ILegalInfoProps): JSX.Element => {
  const location = useLocation()
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  return (
    <div className={`legal-infos ${className}`}>
      <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
      <a
        className="quaternary-link"
        href="https://pass.culture.fr/cgu-professionnels/"
        onClick={() =>
          logEvent(Events.CLICKED_CONSULT_CGU, { from: location.pathname })
        }
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
        onClick={() =>
          logEvent(Events.CLICKED_PERSONAL_DATA, { from: location.pathname })
        }
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
        onClick={() =>
          logEvent(Events.CLICKED_CONSULT_SUPPORT, { from: location.pathname })
        }
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-email-red" />
        <span>contactez notre support.</span>
      </a>
    </div>
  )
}

export default LegalInfos

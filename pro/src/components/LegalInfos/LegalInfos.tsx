import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ExternalSiteRedFilledIcon } from 'icons'
import fullMailIcon from 'icons/full-mail.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

interface ILegalInfoProps {
  title: string
  className: string
}

const LegalInfos = ({ title, className }: ILegalInfoProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  return (
    <div className={`legal-infos ${className}`}>
      <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
      <a
        className="quaternary-link"
        href="https://pass.culture.fr/cgu-professionnels/"
        onClick={() =>
          logEvent?.(Events.CLICKED_CONSULT_CGU, { from: location.pathname })
        }
        rel="noopener noreferrer"
        target="_blank"
      >
        <ExternalSiteRedFilledIcon className="icon-legal-infos" />
        <span>Conditions Générales d’Utilisation</span>
      </a>
      <span>{' ainsi que notre '}</span>
      <a
        className="quaternary-link"
        href="https://pass.culture.fr/donnees-personnelles/"
        onClick={() =>
          logEvent?.(Events.CLICKED_PERSONAL_DATA, { from: location.pathname })
        }
        rel="noopener noreferrer"
        target="_blank"
      >
        <ExternalSiteRedFilledIcon className="icon-legal-infos" />
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
          logEvent?.(Events.CLICKED_CONSULT_SUPPORT, {
            from: location.pathname,
          })
        }
        rel="noopener noreferrer"
        target="_blank"
      >
        <SvgIcon src={fullMailIcon} alt="" className="icon-legal-infos" />
        <span>Contacter notre support.</span>
      </a>
    </div>
  )
}

export default LegalInfos

import React from 'react'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import Icon from 'components/layout/Icon'
import './OperationProcedures.scss'

const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const analytics = useAnalytics()
  return (
    <div className="sign-up-operating-procedures">
      <div>
        Nous vous invitons à prendre connaissance des modalités de
        fonctionnement avant de renseigner les champs suivants.
      </div>
      <a
        className="tertiary-link"
        href="https://passculture.zendesk.com/hc/fr/articles/4411999179665"
        onClick={() => analytics.logHelpCenterClick(location.pathname)}
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        <span>Consulter notre centre d’aide</span>
      </a>
    </div>
  )
}

export default OperatingProcedures

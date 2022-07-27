import './OperationProcedures.scss'

import React from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { Events } from 'core/FirebaseEvents/constants'
import { RootState } from 'store/reducers'

const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const logEvent = useSelector((state: RootState) => state.app.logEvent)

  return (
    <div className="sign-up-operating-procedures">
      <div>
        Nous vous invitons à prendre connaissance des modalités de
        fonctionnement avant de renseigner les champs suivants.
      </div>
      <a
        className="tertiary-link"
        href="https://passculture.zendesk.com/hc/fr/articles/4411999179665"
        onClick={() =>
          logEvent(Events.CLICKED_HELP_CENTER, { from: location.pathname })
        }
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

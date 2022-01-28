import React, { useCallback } from 'react'
import { useLocation } from 'react-router'

import { Title } from 'ui-kit'

import { ReactComponent as InfoIcon } from './assets/info.svg'
import RouteLeavingGuard from './RouteLeavingGuard'
import styles from './RouteLeavingGuardOfferCreation.module.scss'

const RouteLeavingGuardOfferCreation = ({
  when,
}: {
  when: boolean
}): JSX.Element => {
  const location = useLocation()

  const shouldBlockNavigation = useCallback(
    nextLocation => {
      const offerCreationPath = '/offres/creation'
      const stocksPathRegex = /\/offres\/([A-Z0-9]+)\/stocks/g
      const confirmationPathRegex = /\/offres\/([A-Z0-9]+)\/confirmation/g

      if (
        (location.pathname.match(stocksPathRegex) &&
          nextLocation.pathname.startsWith(offerCreationPath)) ||
        (location.pathname.match(offerCreationPath) &&
          nextLocation.pathname.match(confirmationPathRegex))
      ) {
        nextLocation.pathname = '/offres'
        nextLocation.search = ''
        return true
      }
      if (location.pathname.match(confirmationPathRegex)) {
        if (nextLocation.pathname.match(stocksPathRegex)) {
          nextLocation.pathname = '/offres'
          nextLocation.search = ''
        }
        return false
      }
      if (
        nextLocation.pathname.match(stocksPathRegex) ||
        nextLocation.pathname.match(confirmationPathRegex) ||
        (location.pathname.startsWith(offerCreationPath) &&
          nextLocation.pathname.startsWith(offerCreationPath))
      ) {
        return false
      }
      return true
    },
    [location]
  )
  return (
    <RouteLeavingGuard
      extraClassNames={styles['exit-offer-creation-dialog']}
      labelledBy="LEAVING_OFFER_CREATION_LABEL_ID"
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
    >
      <>
        <InfoIcon className={styles['route-leaving-guard-icon']} />
        <Title level={3}>Voulez-vous quitter la création d’offre ?</Title>
        <p>
          Votre offre ne sera pas sauvegardée et toutes les informations seront
          perdues.
        </p>
      </>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferCreation

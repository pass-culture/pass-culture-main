import React, { useCallback } from 'react'
import { useLocation } from 'react-router'

import { Title } from 'ui-kit'

import { ReactComponent as InfoIcon } from './assets/info.svg'
import RouteLeavingGuard from './RouteLeavingGuard'
import styles from './RouteLeavingGuardOfferCreation.module.scss'

const RouteLeavingGuardOfferCreation = ({
  when = true,
  isCollectiveFlow = false,
}: {
  when?: boolean
  isCollectiveFlow?: boolean
}): JSX.Element => {
  const location = useLocation()

  const shouldBlockNavigation = useCallback(
    nextLocation => {
      const offerCreationPath = isCollectiveFlow
        ? '/offre/creation/collectif'
        : '/offre/creation/individuel'
      const stocksPathRegex = isCollectiveFlow
        ? /\/offre\/([A-Z0-9]+)\/collectif\/stocks/g
        : /\/offre\/([A-Z0-9]+)\/individuel\/stocks/g
      const confirmationPathRegex = isCollectiveFlow
        ? /\/offre\/([A-Z0-9]+)\/scolaire\/confirmation/g
        : /\/offres\/([A-Z0-9]+)\/confirmation/g

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
    [location, isCollectiveFlow]
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

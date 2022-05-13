import React, { useCallback } from 'react'

import { IShouldBlockNavigationReturnValue } from './RouteLeavingGuard/RouteLeavingGuard'
import { ReactComponent as InfoIcon } from './assets/info.svg'
import RouteLeavingGuard from './RouteLeavingGuard'
import { Title } from 'ui-kit'
import styles from './RouteLeavingGuardOfferCreation.module.scss'
import { useLocation } from 'react-router-dom'

const RouteLeavingGuardOfferCreation = ({
  when = true,
  isCollectiveFlow = false,
}: {
  when?: boolean
  isCollectiveFlow?: boolean
}): JSX.Element => {
  const location = useLocation()

  const shouldBlockNavigation = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
      let redirectPath = null
      const offerCreationPath = isCollectiveFlow
        ? '/offre/creation/collectif'
        : '/offre/creation/individuel'
      const stocksPathRegex = isCollectiveFlow
        ? /\/offre\/([A-Z0-9]+)\/collectif\/stocks/g
        : /\/offre\/([A-Z0-9]+)\/individuel\/stocks/g
      const confirmationPathRegex = isCollectiveFlow
        ? /\/offre\/([A-Z0-9]+)\/collectif\/confirmation/g
        : /\/offre\/([A-Z0-9]+)\/individuel\/confirmation/g

      if (
        (location.pathname.match(stocksPathRegex) &&
          nextLocation.pathname.startsWith(offerCreationPath)) ||
        (location.pathname.match(offerCreationPath) &&
          nextLocation.pathname.match(confirmationPathRegex))
      ) {
        redirectPath = '/offres'
        return { redirectPath, shouldBlock: true }
      }
      if (location.pathname.match(confirmationPathRegex)) {
        if (nextLocation.pathname.match(stocksPathRegex)) {
          redirectPath = '/offres'
        }
        return { redirectPath, shouldBlock: false }
      }
      if (
        nextLocation.pathname.match(stocksPathRegex) ||
        nextLocation.pathname.match(confirmationPathRegex) ||
        (location.pathname.startsWith(offerCreationPath) &&
          nextLocation.pathname.startsWith(offerCreationPath))
      ) {
        return { shouldBlock: false }
      }
      return { shouldBlock: true }
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

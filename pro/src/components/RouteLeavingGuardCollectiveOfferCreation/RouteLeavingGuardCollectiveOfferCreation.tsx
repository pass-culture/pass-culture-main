import {
  BlockerFunction,
  RouteLeavingGuard,
} from 'components/RouteLeavingGuard/RouteLeavingGuard'

interface RouteLeavingGuardCollectiveOffer {
  when: boolean
}

export const RouteLeavingGuardCollectiveOfferCreation = ({
  when,
}: RouteLeavingGuardCollectiveOffer): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = ({
    currentLocation,
    nextLocation,
  }) => when && currentLocation.pathname !== nextLocation.pathname

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Les informations non enregistrées seront perdues"
      leftButton="Quitter la page"
      rightButton="Rester sur la page"
      closeModalOnRightButton
    />
  )
}

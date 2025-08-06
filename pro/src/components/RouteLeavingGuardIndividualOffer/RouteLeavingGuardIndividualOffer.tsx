import {
  BlockerFunction,
  RouteLeavingGuard,
} from '@/components/RouteLeavingGuard/RouteLeavingGuard'

interface RouteLeavingGuardIndividualOfferProps {
  when: boolean
}

export const RouteLeavingGuardIndividualOffer = ({
  when,
}: RouteLeavingGuardIndividualOfferProps): JSX.Element => {
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

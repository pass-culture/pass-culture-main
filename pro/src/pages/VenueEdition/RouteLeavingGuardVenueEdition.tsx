import {
  BlockerFunction,
  RouteLeavingGuard,
} from '@/components/RouteLeavingGuard/RouteLeavingGuard'

interface RouteLeavingGuardVenueEditionProps {
  shouldBlock: boolean
}

export const RouteLeavingGuardVenueEdition = ({
  shouldBlock,
}: RouteLeavingGuardVenueEditionProps): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => shouldBlock

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

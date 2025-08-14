import { useLocation } from 'react-router'

import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

export interface ActionBarEditionProps {
  onCancel?: () => void
}

export const ActionBarEdition = ({ onCancel }: ActionBarEditionProps) => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const Left = (): JSX.Element => {
    return (
      <Button
        type="button"
        onClick={onCancel}
        variant={ButtonVariant.SECONDARY}
      >
        Annuler et quitter
      </Button>
    )
  }

  const Right = (): JSX.Element => {
    return (
      <Button type="submit" variant={ButtonVariant.PRIMARY}>
        Enregistrer les modifications et quitter
      </Button>
    )
  }

  return (
    <ActionsBarSticky hasSideNav={!isOnboarding}>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right>{Right()}</ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

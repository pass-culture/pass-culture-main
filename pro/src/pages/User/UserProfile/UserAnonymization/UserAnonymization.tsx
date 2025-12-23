import { useState } from 'react'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Dialog } from '@/components/Dialog/Dialog'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { UserAnonymizationForm } from './components/UserAnonymizationForm'
import { UserAnonymizationUneligibility } from './components/UserAnonymizationUneligibility'
import { useUserAnonymizationEligibility } from './hooks/useUserAnonymizationEligibility'

export const UserAnonymization = (): JSX.Element | null => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const canDisplayAnonymizeButton = useActiveFeature(
    'WIP_PRO_AUTONOMOUS_ANONYMIZATION'
  )

  const { isLoading, isEligible, isSoleUserWithOngoingActivities } =
    useUserAnonymizationEligibility()

  if (isLoading || !canDisplayAnonymizeButton) {
    return null
  }

  return (
    <Dialog
      onCancel={() => setIsDialogOpen(false)}
      title={
        isEligible
          ? 'Vous êtes sur le point de supprimer votre compte'
          : 'La suppression de compte n’est pas possible en l’état'
      }
      icon={strokeWarningIcon}
      open={isDialogOpen}
      trigger={
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullTrashIcon}
          onClick={() => setIsDialogOpen(true)}
        >
          Supprimer mon compte
        </Button>
      }
    >
      {isEligible ? (
        <UserAnonymizationForm />
      ) : (
        <UserAnonymizationUneligibility
          isSoleUserWithOngoingActivities={isSoleUserWithOngoingActivities}
        />
      )}
    </Dialog>
  )
}

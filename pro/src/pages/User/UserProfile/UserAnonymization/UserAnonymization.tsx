import { useState } from 'react'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Dialog } from '@/components/Dialog/Dialog'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'

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
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullTrashIcon}
          onClick={() => setIsDialogOpen(true)}
          label="Supprimer mon compte"
        />
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

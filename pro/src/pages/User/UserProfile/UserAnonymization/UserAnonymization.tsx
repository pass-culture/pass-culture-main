import { useState } from 'react'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'

import { UserAnonymizationForm } from './components/UserAnonymizationForm'
import { UserAnonymizationUneligibility } from './components/UserAnonymizationUneligibility'
import { useUserAnonymizationEligibility } from './hooks/useUserAnonymizationEligibility'

export const UserAnonymization = (): JSX.Element | null => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const canDisplayAnonymizeButton = useActiveFeature(
    'PRO_AUTONOMOUS_ANONYMIZATION'
  )

  const { isLoading, isEligible, isSoleUserWithOngoingActivities } =
    useUserAnonymizationEligibility()

  if (isLoading || !canDisplayAnonymizeButton) {
    return null
  }

  return (
    <>
      <Button
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={fullTrashIcon}
        onClick={() => setIsDialogOpen(true)}
        label="Supprimer mon compte"
      />
      <SimpleModal
        iconPath={strokeWarningIcon}
        title={
          isEligible
            ? 'Vous êtes sur le point de supprimer votre compte'
            : 'La suppression de compte n’est pas possible en l’état'
        }
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
      >
        {isEligible ? (
          <UserAnonymizationForm onClose={() => setIsDialogOpen(false)} />
        ) : (
          <UserAnonymizationUneligibility
            isSoleUserWithOngoingActivities={isSoleUserWithOngoingActivities}
            onClose={() => setIsDialogOpen(false)}
          />
        )}
      </SimpleModal>
    </>
  )
}

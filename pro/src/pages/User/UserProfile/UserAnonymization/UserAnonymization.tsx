import { api } from '@/apiClient/api'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useNotification } from '@/commons/hooks/useNotification'
import { logout } from '@/commons/store/user/dispatchers/logout'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

export const UserAnonymization = (): JSX.Element | null => {
  const dispatch = useAppDispatch()
  const notify = useNotification()

  const canDisplayAnonymizeButton = useActiveFeature(
    'WIP_PRO_AUTONOMOUS_ANONYMIZATION'
  )

  if (!canDisplayAnonymizeButton) {
    return null
  }

  return (
    <Button
      variant={ButtonVariant.TERNARY}
      icon={fullTrashIcon}
      onClick={async () => {
        try {
          await api.anonymize()
          dispatch(logout())
        } catch {
          notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
        }
      }}
    >
      Supprimer mon compte
    </Button>
  )
}

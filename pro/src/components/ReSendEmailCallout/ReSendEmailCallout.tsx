import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Banner } from '@/design-system/Banner/Banner'
import fullRefreshIcon from '@/icons/full-refresh.svg'

import styles from './ReSendEmailCallout.module.scss'

export const ReSendEmailCallout = ({
  action,
  hideLink = false,
}: {
  action?: () => Promise<void>
  hideLink?: boolean
}) => {
  const snackBar = useSnackBar()

  const onClick = () => {
    action?.()
      .then(() => {
        snackBar.success('Email envoyé.')
      })
      .catch(() => {
        snackBar.error(
          `Une erreur est survenue, veuillez réessayer ultérieurement.`
        )
      })
  }

  return (
    <Banner
      title="Email non reçu ?"
      actions={
        hideLink
          ? []
          : [
              {
                label: 'Renvoyer un nouveau lien',
                icon: fullRefreshIcon,
                type: 'button',
                href: '',
                onClick,
              },
            ]
      }
      description={
        <p className={styles['re-send-callout']}>
          Vérifiez vos spams{!hideLink && ' ou déclencher un nouvel envoi'}.
        </p>
      }
    />
  )
}

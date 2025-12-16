import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

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
      description={
        <p className={styles['re-send-callout']}>
          Vérifiez vos spams
          {hideLink ? (
            '.'
          ) : (
            <>
              {' '}
              ou{' '}
              <Button
                variant={ButtonVariant.QUATERNARY}
                className={styles['re-send-callout-button']}
                onClick={onClick}
              >
                cliquez ici
              </Button>{' '}
              pour le recevoir à nouveau.
            </>
          )}
        </p>
      }
    />
  )
}

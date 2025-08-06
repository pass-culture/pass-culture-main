import { useNotification } from '@/commons/hooks/useNotification'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'

import styles from './ReSendEmailCallout.module.scss'

export const ReSendEmailCallout = ({
  action,
  hideLink = false,
}: {
  action?: () => Promise<any>
  hideLink?: boolean
}) => {
  const notification = useNotification()

  const onClick = () => {
    action &&
      action()
        .then(() => {
          notification.information('Email renvoyé !')
        })
        .catch(() => {
          notification.error(
            `Une erreur est survenue, veuillez réessayer ultérieurement.`
          )
        })
  }

  return (
    <Callout>
      <p className={styles['re-send-callout']}>
        Vous n’avez pas reçu d’email ? <br /> Vérifiez vos spams
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
    </Callout>
  )
}

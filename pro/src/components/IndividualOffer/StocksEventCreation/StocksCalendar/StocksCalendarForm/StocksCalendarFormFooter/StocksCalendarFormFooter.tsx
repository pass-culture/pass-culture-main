import * as Dialog from '@radix-ui/react-dialog'

import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './StocksCalendarFormFooter.module.scss'

export function StocksCalendarFormFooter() {
  return (
    <div className={styles['footer-container']}>
      <Dialog.Close asChild>
        <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
      </Dialog.Close>
      <Button type="submit">Valider</Button>
    </div>
  )
}

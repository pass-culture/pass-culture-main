import { useRef } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useFunctionOnce } from '@/commons/hooks/useFunctionOnce'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCopyIcon from '@/icons/full-duplicate.svg'

import { Button } from '../Button/Button'
import { ButtonVariant } from '../Button/types'
import styles from './ShareLink.module.scss'

export type ShareLinkProps = {
  link: string
  label: string
  notifySuccessMessage: string
  offerId: number
}

export const ShareLink = ({
  link,
  label,
  notifySuccessMessage,
  offerId,
}: ShareLinkProps) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const logCopyEvent = useFunctionOnce(() => {
    logEvent(Events.CLICKED_COPY_TEMPLATE_OFFER_LINK, {
      from: location.pathname,
      offerId,
    })
  })

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(link)
      snackBar.success(notifySuccessMessage)
      logCopyEvent()
    } catch {
      if (inputRef.current) {
        inputRef.current.select()
        document.execCommand('copy')
        snackBar.success(notifySuccessMessage)
        logCopyEvent()
      }
    }
  }

  return (
    <div className={styles['share-link']}>
      <div className={styles['share-link-input']}>
        <TextInput
          name="share-link"
          label={label}
          value={link}
          ref={inputRef}
        />
      </div>
      <Button
        onClick={handleCopy}
        variant={ButtonVariant.PRIMARY}
        className={styles['share-link-button']}
        icon={fullCopyIcon}
      >
        Copier
      </Button>
    </div>
  )
}

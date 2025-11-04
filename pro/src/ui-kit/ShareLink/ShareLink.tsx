import { useRef } from 'react'

import { useNotification } from '@/commons/hooks/useNotification'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCopyIcon from '@/icons/full-duplicate.svg'

import { Button } from '../Button/Button'
import { ButtonVariant } from '../Button/types'
import styles from './ShareLink.module.scss'

export type ShareLinkProps = {
  link: string
  label: string
  notifySuccessMessage: string
}

export const ShareLink = ({
  link,
  label,
  notifySuccessMessage,
}: ShareLinkProps) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const notify = useNotification()

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(link)
      notify.success(notifySuccessMessage)
    } catch {
      if (inputRef.current) {
        inputRef.current.select()
        document.execCommand('copy')
        notify.success(notifySuccessMessage)
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

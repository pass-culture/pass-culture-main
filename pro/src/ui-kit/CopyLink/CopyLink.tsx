import React, { useState } from 'react'

import fullDuplicate from 'icons/full-duplicate.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button/Button'

import styles from './CopyLink.module.scss'

export interface CopyLinkProps {
  textToCopy: string
}

export const copyTextToClipboard = async (text: string) => {
  if ('clipboard' in navigator) {
    await navigator.clipboard.writeText(text)
  } else {
    document.execCommand('copy', true, text)
  }
}

const CopyLink = ({ textToCopy }: CopyLinkProps): JSX.Element => {
  const [isClicked, setIsClicked] = useState(false)

  return (
    <div
      className={styles['copie-me-box']}
      onClick={() => copyTextToClipboard(textToCopy)}
    >
      <p className={styles['code']}>{textToCopy}</p>
      <Button
        className={
          isClicked ? styles['has-clicked-copy'] : styles['copie-button']
        }
        onClick={() => {
          setIsClicked(true)
          setTimeout(() => {
            setIsClicked(false)
          }, 2900)
        }}
        icon={isClicked ? fullValidateIcon : fullDuplicate}
      >
        {isClicked ? <>Copié</> : <>Copier</>}
      </Button>
    </div>
  )
}

export default CopyLink

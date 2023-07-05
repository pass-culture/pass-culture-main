import React, { useState } from 'react'

import fullDuplicate from 'icons/full-duplicate.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button'

import styles from './CopyLink.module.scss'

export interface CopyLinkProps {
  textToCopy: string
}

const CopyLink = ({ textToCopy }: CopyLinkProps): JSX.Element => {
  const [isClicked, setIsClicked] = useState(false)

  const copyTextToClipboard = async (text: string) => {
    if ('clipboard' in navigator) {
      return await navigator.clipboard.writeText(text).then()
    } else {
      return document.execCommand('copy', true, text)
    }
  }

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

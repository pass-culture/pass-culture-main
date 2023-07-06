import React, { useState } from 'react'

import { ReactComponent as FullDuplicateIcon } from 'icons/full-duplicate.svg'
import { ReactComponent as FullValidateIcon } from 'icons/full-validate.svg'
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
        Icon={isClicked ? FullValidateIcon : FullDuplicateIcon}
      >
        {isClicked ? <>Copié</> : <>Copier</>}
      </Button>
    </div>
  )
}

export default CopyLink

import React, { useState } from 'react'

import Icon from 'components/layout/Icon'
import { Button } from 'ui-kit/Button'

import styles from './CopyLink.module.scss'

export interface ICopyLink {
  textToCopy: string
}

const CopyLink = ({ textToCopy }: ICopyLink): JSX.Element => {
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
      >
        {isClicked ? (
          <>
            <Icon className={styles['icon-button']} svg="ico-is-valid" />
            Copié
          </>
        ) : (
          <>
            <Icon className={styles['icon-button']} svg="ico-copy" />
            Copier
          </>
        )}
      </Button>
    </div>
  )
}

export default CopyLink

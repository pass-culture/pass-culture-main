import React from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Unavailable.module.scss'

export const Unavailable = () => {
  return (
    <main className={styles['unavailable-page']} id="content">
      <SvgIcon className={styles['error-icon']} src={strokeWipIcon} alt="" />
      <h1 className={styles['title']}>Page indisponible</h1>
      <p>Veuillez rééssayer plus tard</p>
    </main>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Unavailable

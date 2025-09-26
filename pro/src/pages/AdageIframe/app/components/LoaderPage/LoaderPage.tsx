import { type JSX, useId } from 'react'

import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './LoaderPage.module.scss'

export const LoaderPage = (): JSX.Element => {
  const contentId = useId()
  return (
    <main className={styles['loader-page']} id={contentId}>
      <Spinner className={styles['loading-spinner']} />
    </main>
  )
}

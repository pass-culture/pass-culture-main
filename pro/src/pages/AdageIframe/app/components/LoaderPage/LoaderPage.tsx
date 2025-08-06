import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './LoaderPage.module.scss'

export const LoaderPage = (): JSX.Element => (
  <main className={styles['loader-page']} id="content">
    {' '}
    <Spinner className={styles['loading-spinner']} />
  </main>
)

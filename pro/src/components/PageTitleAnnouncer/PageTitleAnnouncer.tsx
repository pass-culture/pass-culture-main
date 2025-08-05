import styles from './PageTitleAnnouncer.module.scss'

export const PageTitleAnnouncer = (): JSX.Element => {
  return (
    <div
      id="page-title-announcer"
      aria-live="assertive"
      className={styles['visually-hidden']}
      data-testid="page-title-announcer"
    />
  )
}

import styles from './ScrollContainer.module.scss'

type ScrollContainerProps = {
  containerRef: React.RefObject<HTMLDivElement>
  liveMessage: string
  children: React.ReactNode
  className?: string
}

export const ScrollContainer = ({
  containerRef,
  liveMessage,
  children,
  className,
}: ScrollContainerProps): JSX.Element => {
  return (
    <div ref={containerRef} tabIndex={-1} className={className}>
      <output aria-live="polite" className={styles['visually-hidden']}>
        {liveMessage}
      </output>
      {children}
    </div>
  )
}

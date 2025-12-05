import styles from './AccessibleScrollContainer.module.scss'

type AccessibleScrollContainerProps = {
  containerRef: React.RefObject<HTMLDivElement>
  liveMessage: string
  children: React.ReactNode
  className?: string
}

export const AccessibleScrollContainer = ({
  containerRef,
  liveMessage,
  children,
  className,
}: AccessibleScrollContainerProps): JSX.Element => {
  return (
    <div ref={containerRef} tabIndex={-1} className={className}>
      <output aria-live="polite" className={styles['visually-hidden']}>
        {liveMessage}
      </output>
      {children}
    </div>
  )
}

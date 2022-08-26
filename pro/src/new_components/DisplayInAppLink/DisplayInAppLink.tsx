import React, { FunctionComponent, useCallback, MouseEventHandler } from 'react'

export interface IDisplayInAppLinkProps {
  className?: string
  link: string
  children?: React.ReactNode
  tracking?: { isTracked: boolean; trackingFunction: () => void }
}

export const DisplayInAppLink: FunctionComponent<IDisplayInAppLinkProps> = ({
  className,
  link,
  children,
  tracking,
}) => {
  const openWindow: MouseEventHandler = useCallback(
    event => {
      event.preventDefault()

      window
        .open(link, 'targetWindow', 'toolbar=no, width=375, height=667')
        ?.focus()

      if (tracking?.isTracked) {
        tracking.trackingFunction()
      }
    },
    [link]
  )

  return (
    <a
      className={className}
      href={link}
      onClick={openWindow}
      rel="noopener noreferrer"
      target="_blank"
    >
      {children}
    </a>
  )
}

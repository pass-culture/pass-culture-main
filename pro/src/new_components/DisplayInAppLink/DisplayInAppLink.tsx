import React, { FunctionComponent, useCallback } from 'react'

interface Props {
  className?: string
  link: string
}

export const DisplayInAppLink: FunctionComponent<Props> = ({
  className,
  link,
  children,
}) => {
  const openWindow = useCallback(
    event => {
      event.preventDefault()

      window
        .open(link, 'targetWindow', 'toolbar=no,width=375,height=667')
        ?.focus()
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

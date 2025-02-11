import React, { useEffect, useState } from 'react'

export const useTooltipProps = ({
  onMouseOver,
  onMouseOut,
  onFocus,
  onBlur,
}: Partial<React.HTMLProps<HTMLElement>>) => {
  const [isTooltipHidden, setIsTooltipHidden] = useState(true)

  useEffect(() => {
    const closeTooltipOnEscapePressed = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsTooltipHidden(true)
        event.stopPropagation()
      }
    }
    document.addEventListener('keydown', closeTooltipOnEscapePressed)

    return () => {
      document.removeEventListener('keydown', closeTooltipOnEscapePressed)
    }
  }, [])

  return {
    isTooltipHidden,
    onMouseOver: (event: React.MouseEvent<HTMLElement>) => {
      setIsTooltipHidden(false)
      onMouseOver?.(event)
    },
    onMouseOut: (event: React.MouseEvent<HTMLElement>) => {
      setIsTooltipHidden(true)
      onMouseOut?.(event)
    },
    onFocus: (
      event: React.FocusEvent<HTMLButtonElement | HTMLAnchorElement>
    ) => {
      setIsTooltipHidden(false)
      onFocus?.(event)
    },
    onBlur: (
      event: React.FocusEvent<HTMLButtonElement | HTMLAnchorElement>
    ) => {
      setIsTooltipHidden(true)
      onBlur?.(event)
    },
  }
}

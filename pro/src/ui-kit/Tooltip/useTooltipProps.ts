import React, { useState } from 'react'

export const useTooltipProps = ({
  onMouseOver,
  onMouseOut,
  onFocus,
  onBlur,
  onKeyDown,
}: Partial<React.HTMLProps<HTMLButtonElement | HTMLAnchorElement>>) => {
  const [isTooltipHidden, setIsTooltipHidden] = useState(false)

  return {
    isTooltipHidden,
    onMouseOver: (
      event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>
    ) => {
      setIsTooltipHidden(false)
      onMouseOver?.(event)
    },
    onMouseOut: (
      event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>
    ) => {
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
    onKeyDown: (
      event: React.KeyboardEvent<HTMLButtonElement | HTMLAnchorElement>
    ) => {
      if (event.key === 'Escape' && !isTooltipHidden) {
        setIsTooltipHidden(true)
        event.stopPropagation()
      }
      onKeyDown?.(event)
    },
  }
}

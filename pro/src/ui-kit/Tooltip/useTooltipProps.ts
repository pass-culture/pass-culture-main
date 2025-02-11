import { useEffect, useState } from 'react'

export const useTooltipProps = () => {
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
    onMouseOver: () => {
      setIsTooltipHidden(false)
    },
    onMouseOut: () => {
      setIsTooltipHidden(true)
    },
    onFocus: () => {
      setIsTooltipHidden(false)
    },
    onBlur: () => {
      setIsTooltipHidden(true)
    },
  }
}

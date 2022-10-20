import React, { RefObject, useEffect, useState } from 'react'

const useTooltipMargin = (
  tooltipRef: RefObject<HTMLDivElement>,
  children: React.ReactNode | React.ReactNode[]
) => {
  const [tooltipMargin, setTooltipMargin] = useState<string>()

  // move tooltip above the button relatively to the height of the tooltip and the button
  useEffect(() => {
    if (tooltipRef.current) {
      const tooltipArrowHeight = 4
      const marginToButton = 6
      const tooltipOffset =
        tooltipRef.current.offsetHeight + tooltipArrowHeight + marginToButton
      setTooltipMargin(`-${tooltipOffset}px`)
    }
  }, [children, tooltipRef])

  return tooltipMargin
}

export default useTooltipMargin

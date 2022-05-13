import React from 'react'
import cn from 'classnames'

interface IOfferFormLayoutTitleBlockProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutTitleBlock = ({
  children,
  className,
}: IOfferFormLayoutTitleBlockProps): JSX.Element => (
  <div className={cn(className)}>{children}</div>
)

export default OfferFormLayoutTitleBlock

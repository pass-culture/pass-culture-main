import React from 'react'
import './OfferSection.scss'

export const OfferSection = ({
  title,
  children,
}: {
  title: string
  children: React.ReactNode | React.ReactNode[]
}): JSX.Element => {
  return (
    <section className="offer-details-section">
      <h4 className="offer-details-section-title">{title}</h4>
      {children}
    </section>
  )
}

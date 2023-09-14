import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

interface VenueStatProps {
  count?: string
  label: string
  link: {
    pathname: string
    state?: {
      statuses: string[]
    }
    alt: string
  }
  onClick: () => void
}

const VenueStat = ({ count, label, link, onClick }: VenueStatProps) => (
  <div className="h-card-col" data-testid="venue-stat">
    {
      /* istanbul ignore next: DEBT, TO FIX */ count ? (
        <div className="venue-stat-count">{count}</div>
      ) : (
        <Spinner />
      )
    }
    <div>{label}</div>
    <ButtonLink
      variant={ButtonVariant.TERNARYPINK}
      link={{
        to: `${link.pathname}`,
        isExternal: false,
        'aria-label': link.alt,
      }}
      onClick={onClick}
    >
      Voir
    </ButtonLink>
  </div>
)

export default VenueStat

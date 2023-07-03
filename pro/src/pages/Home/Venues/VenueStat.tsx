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
      className="tertiary-link"
      variant={ButtonVariant.TERNARY}
      link={{
        to: `${link.pathname}`,
        isExternal: false,
      }}
      onClick={onClick}
    >
      Voir
    </ButtonLink>
  </div>
)

export default VenueStat

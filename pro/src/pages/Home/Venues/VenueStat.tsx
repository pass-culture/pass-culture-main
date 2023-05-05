import React from 'react'

import { ReactComponent as LoaderSvg } from 'icons/ico-passculture.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IVenueStatProps {
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
const VenueStat = ({ count, label, link, onClick }: IVenueStatProps) => (
  <div className="h-card-col" data-testid="venue-stat">
    {
      /* istanbul ignore next: DEBT, TO FIX */ count ? (
        <div className="venue-stat-count">{count}</div>
      ) : (
        <LoaderSvg className="venue-stat-spinner" title="Chargement en cours" />
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

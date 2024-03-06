import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  return (
    <ButtonLink
      link={{
        to: `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/edition`,
      }}
      variant={ButtonVariant.TERNARY}
    >
      Modifier {venue.name}
    </ButtonLink>
  )
}

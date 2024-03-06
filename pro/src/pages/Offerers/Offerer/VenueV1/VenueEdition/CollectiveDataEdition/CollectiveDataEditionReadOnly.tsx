import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface CollectiveDataEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const CollectiveDataEditionReadOnly = ({
  venue,
}: CollectiveDataEditionReadOnlyProps) => {
  return (
    <ButtonLink
      link={{
        to: `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/eac/edition`,
      }}
      variant={ButtonVariant.TERNARY}
    >
      Modifier {venue.name}
    </ButtonLink>
  )
}

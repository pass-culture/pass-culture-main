import React from 'react'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit'

import { Venue } from './Venue'

export interface IUsefulInformationsProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  isUserAdmin: boolean
}

const UserfulInformations = ({
  offererNames,
  venueList,
  isUserAdmin,
}: IUsefulInformationsProps): JSX.Element => {
  return (
    <FormLayout.Section
      title="Informations pratiques"
      description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
    >
      <Venue offererNames={offererNames} venueList={venueList} />

      {isUserAdmin && (
        <FormLayout.Row>
          <Checkbox
            hideFooter
            label={'Rayonnement national'}
            name="isNational"
            value=""
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default UserfulInformations

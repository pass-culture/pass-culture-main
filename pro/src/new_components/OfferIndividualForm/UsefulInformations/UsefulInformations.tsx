import { useFormikContext } from 'formik'
import React from 'react'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { Checkbox, TextArea } from 'ui-kit'

import { IOfferIndividualFormValues } from '../types'

import { TicketWithdrawal } from './TicketWithdrawal'
import { Venue } from './Venue'

export interface IUsefulInformationsProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  isUserAdmin: boolean
}

const UsefulInformations = ({
  offererNames,
  venueList,
  isUserAdmin,
}: IUsefulInformationsProps): JSX.Element => {
  const {
    values: { subCategoryFields },
  } = useFormikContext<IOfferIndividualFormValues>()

  return (
    <FormLayout.Section
      title="Informations pratiques"
      description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
    >
      <Venue offererNames={offererNames} venueList={venueList} />

      {subCategoryFields.includes('withdrawalType') && <TicketWithdrawal />}

      <FormLayout.Row>
        <TextArea
          countCharacters
          isOptional
          label={'Informations de retrait'}
          name="withdrawalDetails"
          maxLength={500}
        />
      </FormLayout.Row>

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

export default UsefulInformations

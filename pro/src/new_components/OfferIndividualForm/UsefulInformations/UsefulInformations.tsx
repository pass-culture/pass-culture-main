import { Checkbox, TextArea } from 'ui-kit'

import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from '../types'
import { IOfferSubCategory } from 'core/Offers/types'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import { TicketWithdrawal } from './TicketWithdrawal'
import { Venue } from './Venue'
import { useFormikContext } from 'formik'

export interface IUsefulInformationsProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  subCategories: IOfferSubCategory[]
  isUserAdmin: boolean
}

const UsefulInformations = ({
  offererNames,
  venueList,
  subCategories,
  isUserAdmin,
}: IUsefulInformationsProps): JSX.Element => {
  const {
    values: { subcategoryId },
  } = useFormikContext<IOfferIndividualFormValues>()

  const subCategory = subCategories.find(s => s.id === subcategoryId)
  const isEvent = subCategory?.isEvent

  return (
    <FormLayout.Section
      title="Informations pratiques"
      description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
    >
      <Venue offererNames={offererNames} venueList={venueList} />
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

      {isEvent && <TicketWithdrawal subCategories={subCategories} />}
    </FormLayout.Section>
  )
}

export default UsefulInformations

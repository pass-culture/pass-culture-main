import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit/form'
import TextArea from 'ui-kit/form/TextArea'

import { IVenue } from '../../../core/Venue/types'
import { useFormikContext } from 'formik'
import { IVenueFormValues } from '../types'

interface IWithdrawalDetails {
  isCreatedEntity?: boolean
}

const WithdrawalDetails = ({ isCreatedEntity }: IWithdrawalDetails) => {
  const { values } = useFormikContext<IVenueFormValues>()

  return (
    <>
      <FormLayout.Section
        title="Modalités de retrait"
        description="Les modalités de retrait s’appliqueront par défaut à la création de
            vos offres. Vous pourrez modifier cette information à l’échelle de
            l’offre."
      >
        <FormLayout.Row>
          <TextArea
            name="withdrawalDetails"
            label="Modalités de retrait"
            maxLength={500}
            countCharacters
            isOptional
          />
        </FormLayout.Row>
        {!isCreatedEntity && (
          <FormLayout.Row>
            <Checkbox
              name="isWithdrawalAppliedOnAllOffers"
              label="Appliquer le changement à toutes les offres déjà existantes."
            ></Checkbox>
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}
export default WithdrawalDetails

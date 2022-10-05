import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox, TextArea } from 'ui-kit/form'

interface IWithdrawalDetails {
  isCreatedEntity?: boolean
}

const WithdrawalDetails = ({ isCreatedEntity }: IWithdrawalDetails) => {
  return (
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
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}
export default WithdrawalDetails

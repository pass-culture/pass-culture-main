import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { InfoBox } from 'ui-kit'
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
      <FormLayout.Row
        sideComponent={
          <InfoBox
            type="info"
            text="Cela permet aux jeunes une plus grande autonomie lors de la récupération de leurs offres."
            link={{
              text: 'En savoir plus',
              to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
              isExternal: true,
              'aria-label': 'en savoir plus sur les modalités de retrait',
            }}
          />
        }
      >
        <TextArea
          name="withdrawalDetails"
          label="Modalités de retrait"
          maxLength={500}
          placeholder="Par exemple : Venir récuperer les places au guichet du théâtre…"
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

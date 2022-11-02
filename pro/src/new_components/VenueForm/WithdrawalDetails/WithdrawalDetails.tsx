import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { InfoBox } from 'ui-kit'
import { Checkbox, TextArea } from 'ui-kit/form'

interface IWithdrawalDetails {
  isCreatedEntity?: boolean
}

const WithdrawalDetails = ({ isCreatedEntity }: IWithdrawalDetails) => {
  return (
    <FormLayout.Section title="Informations de retrait de vos offres">
      <FormLayout.Row
        sideComponent={
          <InfoBox
            type="info"
            text="Indiquez ici tout ce qui peut être utile au jeune pour le retrait de l’offre. Ces indications s’appliqueront par défaut à toutes vos offres. Vous pourrez les modifier à l’échelle de chaque offre."
            link={{
              text: 'En savoir plus',
              to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
              isExternal: true,
              target: '_blank',
              rel: 'noopener noreferrer',
              'aria-label': 'en savoir plus sur les modalités de retrait',
            }}
          />
        }
      >
        <TextArea
          name="withdrawalDetails"
          label="Informations de retrait"
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

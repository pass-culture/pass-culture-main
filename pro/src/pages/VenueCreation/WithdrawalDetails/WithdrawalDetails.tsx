import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

export const WithdrawalDetails = () => {
  return (
    <FormLayout.Section title="Informations de retrait de vos offres">
      <FormLayout.Row
        sideComponent={
          <InfoBox
            link={{
              text: 'En savoir plus',
              to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
              isExternal: true,
              'aria-label': 'en savoir plus sur les modalités de retrait',
            }}
          >
            Indiquez ici tout ce qui peut être utile au jeune pour le retrait de
            l’offre. Ces indications s’appliqueront par défaut à toutes vos
            offres. Vous pourrez les modifier à l’échelle de chaque offre.
          </InfoBox>
        }
      >
        <TextArea
          name="withdrawalDetails"
          label="Informations de retrait"
          maxLength={500}
          description="Par exemple : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par email..."
          countCharacters
          isOptional
        />
      </FormLayout.Row>

      <FormLayout.Row>
        <Checkbox
          name="isWithdrawalAppliedOnAllOffers"
          label="Appliquer le changement à toutes les offres déjà existantes"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

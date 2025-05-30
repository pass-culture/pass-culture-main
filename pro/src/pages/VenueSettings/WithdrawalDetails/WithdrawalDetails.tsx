import { useFormContext } from 'react-hook-form'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { VenueSettingsFormValues } from '../types'

export const WithdrawalDetails = () => {
  const methods = useFormContext<VenueSettingsFormValues>()
  const { register } = methods

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
            prochaines offres. Pour les offres actuelles, vous devez les
            modifier individuellement.
          </InfoBox>
        }
      >
        <TextArea
          {...register('withdrawalDetails')}
          name="withdrawalDetails"
          label="Informations de retrait"
          maxLength={500}
          description="Par exemple : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par email..."
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

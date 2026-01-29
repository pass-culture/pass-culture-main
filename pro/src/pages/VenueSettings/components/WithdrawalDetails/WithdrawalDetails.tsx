import { useFormContext } from 'react-hook-form'

import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import type { VenueSettingsFormValues } from '../../commons/types'
import styles from '../VenueSettingsScreen.module.scss'

export const WithdrawalDetails = () => {
  const methods = useFormContext<VenueSettingsFormValues>()
  const { register } = methods

  return (
    <FormLayout.Section title="Informations de retrait de vos offres">
      <FormLayout.Row
        sideComponent={
          <TipsBanner>
            <span className={styles['side-text-spacing']}>
              Indiquez ici tout ce qui peut être utile au jeune pour le retrait
              de l’offre. Ces indications s’appliqueront par défaut à toutes vos
              prochaines offres. Pour les offres actuelles, vous devez les
              modifier individuellement.
            </span>
            <Button
              as="a"
              icon={fullLinkIcon}
              variant={ButtonVariant.TERTIARY}
              size={ButtonSize.SMALL}
              label="En savoir plus"
              to="https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-"
              isExternal
              opensInNewTab
              aria-label="en savoir plus sur les modalités de retrait"
            />
          </TipsBanner>
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

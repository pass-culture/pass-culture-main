import { useFormContext } from 'react-hook-form'

import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullInfoIcon from '@/icons/full-info.svg'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import type { VenueSettingsFormValues } from '../../../VenueSettings/GeneralInformation/commons/types'
import styles from './WithdrawalDetails.module.scss'

export const WithdrawalDetails = () => {
  const methods = useFormContext<VenueSettingsFormValues>()
  const { register } = methods

  return (
    <FormLayout.SubSection
      title="Informations de retrait de vos offres"
      className={styles['sub-section']}
    >
      <FormLayout.Row smSpaceAfter>
        <TextArea
          {...register('withdrawalDetails')}
          name="withdrawalDetails"
          label="Informations de retrait"
          maxLength={500}
          description="Par exemple : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par email..."
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <Banner
          title="À savoir"
          description="Ces indications s’appliqueront par défaut à toutes vos prochaines offres."
          variant={BannerVariants.DEFAULT}
          icon={fullInfoIcon}
        />
      </FormLayout.Row>
    </FormLayout.SubSection>
  )
}

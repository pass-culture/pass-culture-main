import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import { toFormValues } from '@/pages/VenueSettings/commons/utils/toFormValues'

import { useSaveVenueSettings } from '../commons/hooks/useSaveVenueSettings'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../commons/types'
import { venueSettingsValidationSchema } from '../commons/validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'
import styles from './VenueSettingsScreen.module.scss'

export interface VenueSettingsScreenProps {
  offerer: GetOffererResponseModel
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  offerer,
  venueProviders,
  venue,
}: VenueSettingsScreenProps): JSX.Element => {
  const navigate = useNavigate()

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    isVenueVirtual: venue.isVirtual,
    siren: offerer.siren,
    withSiret: Boolean(venue.siret),
  }

  const form = useForm<VenueSettingsFormValues>({
    context: formContext,
    defaultValues: toFormValues({ venue }),
    resolver: yupResolver(
      // biome-ignore lint/suspicious/noExplicitAny: TODO : review validation schema
      venueSettingsValidationSchema as any
    ),
    mode: 'onBlur',
  })

  const { saveAndContinue } = useSaveVenueSettings({ form, venue })

  const onSubmit = (formValues: VenueSettingsFormValues) => {
    saveAndContinue(formValues, formContext)
  }

  return (
    <>
      <div className={styles['back-button']}>
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.BRAND}
          icon={fullBackIcon}
          onClick={() => navigate(-1)}
          label="Retour vers la page précédente"
        />
      </div>

      <MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <VenueSettingsForm
            venueProviders={venueProviders}
            venue={venue}
            offerer={offerer}
            formContext={formContext}
          />
        </form>
      </FormProvider>
    </>
  )
}

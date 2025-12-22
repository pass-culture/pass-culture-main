import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import fullBackIcon from '@/icons/full-back.svg'
import { toFormValues } from '@/pages/VenueSettings/commons/utils/toFormValues'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { useSaveVenueSettings } from '../commons/hooks/useSaveVenueSettings'
import type { VenueSettingsFormContext } from '../commons/types'
import {
  type VenueSettingsFormValuesType,
  venueSettingsValidationSchema,
} from '../commons/validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'
import styles from './VenueSettingsScreen.module.scss'

export interface VenueSettingsScreenProps {
  offerer: GetOffererResponseModel
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  offerer,
  venueTypes,
  venueProviders,
  venue,
}: VenueSettingsScreenProps): JSX.Element => {
  const navigate = useNavigate()

  const isVenueActivityFeatureActive = useActiveFeature('WIP_VENUE_ACTIVITY')

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    isVenueVirtual: venue.isVirtual,
    siren: offerer.siren,
    withSiret: Boolean(venue.siret),
    isVenueActivityFeatureActive,
  }

  const form = useForm({
    context: formContext,
    defaultValues: venueSettingsValidationSchema.cast(toFormValues({ venue })),
    resolver: yupResolver(venueSettingsValidationSchema),
    mode: 'onBlur',
  })

  const { saveAndContinue } = useSaveVenueSettings({ form, venue })

  const onSubmit = (formValues: VenueSettingsFormValuesType) => {
    saveAndContinue(formValues, formContext)
  }

  return (
    <>
      <Button
        className={styles['back-button']}
        variant={ButtonVariant.TERNARYBRAND}
        icon={fullBackIcon}
        onClick={() => navigate(-1)}
      >
        Retour vers la page précédente
      </Button>
      <MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <VenueSettingsForm
            venueTypes={venueTypes}
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

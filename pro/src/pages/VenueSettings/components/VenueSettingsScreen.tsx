import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import type {
  GetVenueManagingOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1/new'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { toFormValues } from '@/pages/VenueSettings/commons/utils/toFormValues'

import { useSaveVenueSettings } from '../commons/hooks/useSaveVenueSettings'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../commons/types'
import { venueSettingsValidationSchema } from '../commons/validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'

export interface VenueSettingsScreenProps {
  offerer: GetVenueManagingOffererResponseModel
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  offerer,
  venueProviders,
  venue,
}: VenueSettingsScreenProps): JSX.Element => {
  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    isVenueVirtual: venue.isVirtual ?? false,
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
      <MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <VenueSettingsForm
            venueProviders={venueProviders}
            venue={venue}
            formContext={formContext}
          />
        </form>
      </FormProvider>
    </>
  )
}

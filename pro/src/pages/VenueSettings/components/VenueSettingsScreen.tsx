import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import fullBackIcon from '@/icons/full-back.svg'
import { toFormValues } from '@/pages/VenueSettings/commons/utils/toFormValues'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

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

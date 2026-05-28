import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { RouteLeavingGuardVenueEdition } from '@/pages/VenueEdition/components/RouteLeavingGuardVenueEdition'
import { VenueFormActionBar } from '@/pages/VenueEdition/components/VenueFormActionBar/VenueFormActionBar'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import { useSaveVenueSettings } from '../commons/hooks/useSaveVenueSettings'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../commons/types'
import { toFormValues } from '../commons/utils/toFormValues'
import { venueSettingsValidationSchema } from '../commons/validationSchema'

const Notifications = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    siren: venue.managingOfferer?.siren,
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

  const onSubmit = (formValues: VenueSettingsFormValues) =>
    saveAndContinue(formValues, formContext)

  const {
    register,
    formState: { isDirty, isSubmitting, isSubmitted, errors },
  } = form

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Notifications de réservations">
            <FormLayout.Row lgSpaceAfter>
              <TextInput
                {...register('bookingEmail')}
                label="Adresse email"
                type="email"
                description="Format : email@exemple.com"
                error={errors.bookingEmail?.message}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TipsBanner>
                Cette adresse s’applique par défaut à toutes vos offres, vous
                pouvez la modifier à l’échelle de chaque offre.
              </TipsBanner>
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
        <VenueFormActionBar isSubmitting={isSubmitting} isSettingsPage />
        <RouteLeavingGuardVenueEdition
          shouldBlock={isDirty && !isSubmitting && !isSubmitted}
        />
      </form>
    </FormProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Notifications

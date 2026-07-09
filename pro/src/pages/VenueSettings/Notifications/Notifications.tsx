import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { VenueFormActionBar } from '@/components/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import { scrollToTop } from '../../../commons/utils/scrollToTop'
import { useSave } from './commons/hooks/useSave'
import {
  type VenueSettingsNotificationsFormValues,
  VenueSettingsNotificationsValidationSchema,
} from './commons/schemas'

const Notifications = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const form = useForm<VenueSettingsNotificationsFormValues>({
    defaultValues: {
      bookingEmail: selectedPartnerVenue.bookingEmail,
    },
    resolver: yupResolver(VenueSettingsNotificationsValidationSchema),
    mode: 'onBlur',
  })

  const { save } = useSave({
    form,
    venue: selectedPartnerVenue,
  })

  const onSubmit = (
    formValues: VenueSettingsNotificationsFormValues
  ): Promise<boolean> => {
    const canProceed = save(formValues)

    scrollToTop()

    return canProceed
  }

  const onCancel = () => {
    form.reset()
    scrollToTop()
  }

  const {
    register,
    formState: { isSubmitting, errors },
  } = form

  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({ form, onSubmit })

  return (
    <>
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler} noValidate>
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
          <VenueFormActionBar
            disableFormSubmission={
              withVenueHelpers(selectedPartnerVenue).isClosed
            }
            isSubmitting={isSubmitting}
            onCancel={onCancel}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Notifications

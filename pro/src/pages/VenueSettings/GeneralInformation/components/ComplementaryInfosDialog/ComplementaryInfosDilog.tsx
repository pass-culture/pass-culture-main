import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { FormProvider, useForm } from 'react-hook-form'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OpeningHours } from '@/components/OpeningHours/OpeningHours'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { serializeEditVenueBodyModel } from '@/pages/VenueEdition/commons/serializers'
import { setInitialFormValues } from '@/pages/VenueEdition/commons/setInitialFormValues'
import type { VenueEditionFormValues } from '@/pages/VenueEdition/commons/types'
import { getValidationSchema } from '@/pages/VenueEdition/commons/validationSchema'
import { AccessibilityForm } from '@/pages/VenueEdition/components/AccessibilityForm/AccessibilityForm'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import styles from './ComplementaryInfosDialog.module.scss'

interface ComplementaryInfosDialogProps {
  venue: GetVenueResponseModel
  hasAddressChanged: boolean
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const ComplementaryInfosDialog = ({
  open,
  onOpenChange,
  venue,
  hasAddressChanged,
}: Readonly<ComplementaryInfosDialogProps>) => {
  const { syncVenueWithData } = useSyncVenueCache()

  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const initialValues: VenueEditionFormValues = setInitialFormValues(venue)
  const methods = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema()),
    mode: 'onBlur',
  })

  const onSubmit = async (values: VenueEditionFormValues) => {
    try {
      const updatedVenue = await apiNew.editVenue({
        path: { venue_id: venue.id },
        body: serializeEditVenueBodyModel(
          values,
          !venue.siret,
          venue.openingHours !== null
        ),
      })

      await syncVenueWithData(venue.id, updatedVenue)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      let formErrors: Record<string, string> | undefined
      if (isErrorAPIError(error)) {
        formErrors = error.body
      }

      const errorsKeys = formErrors ? Object.keys(formErrors) : []

      if (
        !formErrors ||
        errorsKeys.length === 0 ||
        errorsKeys.includes('global')
      ) {
        snackBar.error('Erreur inconnue lors de la sauvegarde de la structure.')
      } else {
        snackBar.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )

        for (const field of errorsKeys) {
          methods.setError(field as keyof VenueEditionFormValues, {
            type: field,
            message: formErrors[field].toString(),
          })
        }
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: false,
        isEdition: true,
      })
    }
  }
  return (
    <DialogBuilder
      open={open}
      onOpenChange={onOpenChange}
      title="Informations complémentaires"
      className={styles['dialog']}
    >
      <div className={styles['dialog-description']}>
        Améliorez l'expérience de votre public en précisant vos modalités
        d'accueil et vos horaires.
      </div>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit((values) => onSubmit(values))}>
          <FormLayout>
            <FormLayout.Section>
              <AccessibilityForm
                externalAccessibilityId={venue.externalAccessibilityId}
                externalAccessibilityData={venue.externalAccessibilityData}
                isSubSubSection
              ></AccessibilityForm>
              <FormLayout.SubSection title="Horaires d’ouverture">
                <FormLayout.Row className={styles['opening-hours']}>
                  <fieldset>
                    <div>
                      <OpeningHours />
                    </div>
                  </fieldset>
                </FormLayout.Row>
              </FormLayout.SubSection>
              {hasAddressChanged && (
                <Banner
                  variant={BannerVariants.WARNING}
                  title="Vos offres existantes ne sont pas mises à jour"
                  description="La modification de cette adresse ne change pas automatiquement la localisation de vos offres déjà créées. Pensez à les modifier individuellement."
                ></Banner>
              )}
            </FormLayout.Section>
          </FormLayout>

          <DialogBuilder.Footer>
            <div className={styles['dialog-buttons']}>
              <Dialog.Close asChild>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  label="Annuler"
                />
              </Dialog.Close>
              <Button type="submit" label="Enregistrer les informations" />
            </div>
          </DialogBuilder.Footer>
        </form>
      </FormProvider>
    </DialogBuilder>
  )
}

import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { serializeEditVenueBodyModel } from '@/commons/core/VenueEdition/serializeEditVenueBodyModel'
import { setInitialFormValues } from '@/commons/core/VenueEdition/setInitialFormValues'
import type { VenueEditionFormValues } from '@/commons/core/VenueEdition/types'
import { getValidationSchema } from '@/commons/core/VenueEdition/validationSchema'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { AccessibilityForm } from '@/components/VenueEdition/AccessibilityForm/AccessibilityForm'
import { OpeningHours } from '@/components/VenueEdition/OpeningHours/OpeningHours'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import styles from './ComplementaryInfosDrawer.module.scss'

interface ComplementaryInfosDrawerProps {
  hasAddressChanged: boolean
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const ComplementaryInfosDrawer = ({
  open,
  onOpenChange,
  hasAddressChanged,
}: Readonly<ComplementaryInfosDrawerProps>) => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const { syncVenueWithData } = useSyncVenueCache()

  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const initialValues: VenueEditionFormValues =
    setInitialFormValues(selectedPartnerVenue)
  const methods = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema()),
    mode: 'onBlur',
  })

  const onSubmit = async (values: VenueEditionFormValues) => {
    try {
      const updatedVenue = await api.editVenue({
        path: { venue_id: selectedPartnerVenue.id },
        body: serializeEditVenueBodyModel(
          {
            accessibility: values.accessibility,
            isAccessibilityAppliedOnAllOffers:
              values.isAccessibilityAppliedOnAllOffers,
            openingHours: values.openingHours,
          },
          !selectedPartnerVenue.siret,
          selectedPartnerVenue.openingHours !== null
        ),
      })

      await syncVenueWithData(selectedPartnerVenue.id, updatedVenue)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')
      onOpenChange(false)
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
      onOpenChange={(open) => {
        onOpenChange(open)
        if (!open) {
          methods.reset()
        }
      }}
      title="Informations complémentaires"
      className={styles['dialog']}
      variant="drawer"
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
                externalAccessibilityId={
                  selectedPartnerVenue.externalAccessibilityId
                }
                externalAccessibilityData={
                  selectedPartnerVenue.externalAccessibilityData
                }
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

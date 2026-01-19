import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import type { ManagedVenue } from '@/apiClient/v1'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './PricingPointDialog.module.scss'
import { validationSchema } from './validationSchema'

type PricingPointFormValues = {
  pricingPointId: string
}

type PricingPointDialogProps = {
  selectedVenue: ManagedVenue | null
  venues: ManagedVenue[]
  closeDialog: () => void
  updateVenuePricingPoint: (venueId: number) => void
}

export const PricingPointDialog = ({
  selectedVenue,
  venues,
  closeDialog,
  updateVenuePricingPoint,
}: PricingPointDialogProps) => {
  const snackBar = useSnackBar()

  const methods = useForm<PricingPointFormValues>({
    defaultValues: {
      pricingPointId: undefined,
    },
    resolver: yupResolver(validationSchema),
  })

  const onSubmit = async ({ pricingPointId }: PricingPointFormValues) => {
    if (!selectedVenue) {
      return
    }
    try {
      await api.linkVenueToPricingPoint(selectedVenue.id, {
        pricingPointId: Number(pricingPointId),
      })
      updateVenuePricingPoint(selectedVenue.id)
      closeDialog()

      snackBar.success('Vos modifications ont bien été prises en compte.')
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard')
    }
  }

  if (!selectedVenue) {
    return
  }

  const venuesOptions = [
    {
      label: `Sélectionner le SIRET dans la liste`,
      value: '',
    },
    ...venues.map((venue) => ({
      label: `${venue.name} - ${venue.siret}`,
      value: venue.id.toString(),
    })),
  ]

  return (
    <div className={styles.dialog}>
      <div className={styles['callout']}>
        <Banner
          title="Sélection du SIRET de remboursement"
          description="Choisissez le SIRET qui déterminera votre taux de remboursement pour cette structure. Ce choix sera définitif après validation."
        />
      </div>
      <form
        onSubmit={(event) => {
          // Necessary to prevent the form submission event from bubbling up and potentially triggering parent Dialog close.
          event.stopPropagation()
          methods.handleSubmit(onSubmit)(event)
        }}
        className={styles['dialog-form']}
      >
        <Select
          {...methods.register('pricingPointId')}
          name="pricingPointId"
          label="Structure avec SIRET utilisée pour le calcul du barème de remboursement"
          options={venuesOptions}
          className={styles['venues-select']}
          error={methods.formState.errors.pricingPointId?.message}
        />
        <DialogBuilder.Footer>
          <div className={styles['dialog-actions']}>
            <Dialog.Close asChild>
              <Button
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                label="Annuler"
              />
            </Dialog.Close>
            <Button
              type="submit"
              disabled={methods.formState.isSubmitting}
              label="Valider la sélection"
            />
          </div>
        </DialogBuilder.Footer>
      </form>
    </div>
  )
}

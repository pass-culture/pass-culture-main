import { api } from 'apiClient/api'
import { ManagedVenues } from 'apiClient/v1'
import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useNotification } from 'commons/hooks/useNotification'
import { useForm } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { Select } from 'ui-kit/form/Select/Select'

import styles from './PricingPointDialog.module.scss'
import { validationSchema } from './validationSchema'

type PricingPointFormValues = {
  pricingPointId: string
}

type PricingPointDialogProps = {
  selectedVenue: ManagedVenues | null
  venues: ManagedVenues[]
  closeDialog: () => void
  updateVenuePricingPoint: (venueId: number) => void
}

export const PricingPointDialog = ({
  selectedVenue,
  venues,
  closeDialog,
  updateVenuePricingPoint,
}: PricingPointDialogProps) => {
  const notification = useNotification()

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

      notification.success('Vos modifications ont bien été prises en compte.')
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
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
      <Callout className={styles['callout']}>
        Comme indiqué dans nos CGUs, le barème de remboursement se définit sur
        la base d’un établissement et donc d’un SIRET. Afin de vous faire
        rembourser les offres de cette structure, vous devez sélectionner le
        SIRET à partir duquel sera calculé votre taux de remboursement.
        Attention, vous ne pourrez plus modifier votre choix après validation.{' '}
      </Callout>
      <form
        onSubmit={methods.handleSubmit(onSubmit)}
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
              <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
            </Dialog.Close>
            <Button type="submit" disabled={methods.formState.isSubmitting}>
              Valider la sélection
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </div>
  )
}

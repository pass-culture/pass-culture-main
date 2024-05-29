import { FormikProvider, useFormik } from 'formik'

import { api } from 'apiClient/api'
import { ManagedVenues } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { DialogBox } from 'components/DialogBox/DialogBox'
import useNotification from 'hooks/useNotification'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form/Select/Select'

import styles from './PricingPointDialog.module.scss'
import { validationSchema } from './validationSchema'

type PricingPointFormValues = {
  pricingPointId?: string
}

type PricingPointDialogProps = {
  selectedVenue: ManagedVenues
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
  const formik = useFormik<PricingPointFormValues>({
    initialValues: {
      pricingPointId: undefined,
    },
    onSubmit: async ({ pricingPointId }) => {
      try {
        await api.linkVenueToPricingPoint(selectedVenue.id, {
          pricingPointId: Number(pricingPointId),
        })
        updateVenuePricingPoint(selectedVenue.id)
        closeDialog()
      } catch (e) {
        notification.error(
          'Une erreur est survenue. Merci de réessayer plus tard'
        )
      }
    },
    validationSchema: validationSchema,
  })

  const venuesOptions = [
    { label: 'Sélectionner un lieu dans la liste', value: '' },
    ...venues.map((venue) => ({
      label: `${venue.commonName} - ${venue.siret}`,
      value: venue.id.toString(),
    })),
  ]

  return (
    <DialogBox
      labelledBy="Sélectionner un SIRET"
      extraClassNames={styles.dialog}
      hasCloseButton
      onDismiss={closeDialog}
    >
      <h1 className={styles['callout-title']}>
        Sélectionnez un SIRET pour le lieu “{selectedVenue.commonName}”{' '}
      </h1>
      <Callout
        className={styles['callout']}
        links={[
          {
            href: 'https://aide.passculture.app/hc/fr/articles/4413973462929--Acteurs-Culturels-Comment-rattacher-mes-points-de-remboursement-et-mes-coordonn%C3%A9es-bancaires-%C3%A0-un-SIRET-de-r%C3%A9f%C3%A9rence-',
            isExternal: true,
            label:
              'Comment ajouter vos coordonnées bancaires sur un lieu sans SIRET ?',
          },
        ]}
      >
        Comme indiqué dans nos CGUs, le barème de remboursement se définit sur
        la base d’un établissement et donc d’un SIRET. Afin de vous faire
        rembourser les offres de ce lieu, vous devez sélectionner le SIRET à
        partir duquel sera calculé votre taux de remboursement. Attention, vous
        ne pourrez plus modifier votre choix après validation.{' '}
      </Callout>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} className={styles['dialog-form']}>
          <Select
            id="pricingPointId"
            name="pricingPointId"
            label={
              'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement'
            }
            placeholder="Sélectionnez le SIRET dans la liste"
            options={venuesOptions}
            className={styles['venues-select']}
          />
          <div className={styles['dialog-actions']}>
            <Button variant={ButtonVariant.SECONDARY} onClick={closeDialog}>
              Annuler
            </Button>
            <Button type="submit">Valider la sélection</Button>
          </div>
        </form>
      </FormikProvider>
    </DialogBox>
  )
}

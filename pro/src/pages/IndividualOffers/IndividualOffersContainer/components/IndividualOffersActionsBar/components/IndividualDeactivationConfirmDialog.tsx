import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { NBSP } from '@/commons/core/shared/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import fullEyeIcon from '@/icons/full-hide.svg'

export interface DeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
  isDialogOpen: boolean
}

export const IndividualDeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
  isDialogOpen,
}: DeactivationConfirmDialogProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  return (
    <SimpleModal
      iconPath={fullEyeIcon}
      title={`Vous avez sélectionné ${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre', 'offres')}`}
      isOpen={isDialogOpen}
      onClose={() => {
        logEvent(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
          has_selected_all_offers: areAllOffersSelected,
        })
        onCancel(false)
      }}
      actionButtons={[
        <Button
          onClick={() => {
            logEvent(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
              has_selected_all_offers: areAllOffersSelected,
            })
            onCancel(false)
          }}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler"
          key="cancel"
        />,
        <Button
          onClick={() => {
            logEvent(Events.CLICKED_DISABLED_SELECTED_OFFERS, {
              has_selected_all_offers: areAllOffersSelected,
            })
            onConfirm()
          }}
          label="Mettre en pause"
          key="confirm"
        />,
      ]}
    >
      <p>
        {nbSelectedOffers === 1
          ? `êtes-vous sûr de vouloir la mettre en pause${NBSP}?`
          : `êtes-vous sûr de vouloir toutes les mettre en pause${NBSP}?`}
      </p>
      <p>
        Dans ce cas,{' '}
        {pluralizeFr(
          nbSelectedOffers,
          'elle ne sera plus visible',
          'elles ne seront plus visibles'
        )}{' '}
        sur l’application pass Culture.
      </p>
    </SimpleModal>
  )
}

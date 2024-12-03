import classNames from 'classnames'
import { useCallback, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'commons/core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'commons/core/Offers/constants'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { computeDeletionErrorMessage } from 'pages/IndividualOffers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from 'pages/IndividualOffers/utils/computeDeletionSuccessMessage'
import { computeIndividualApiFilters } from 'pages/IndividualOffers/utils/computeIndividualApiFilters'
import styles from 'styles/components/Cells.module.scss'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'


import { DeleteDraftCell } from './DeleteDraftCell'
import { EditOfferCell } from './EditOfferCell'
import { EditStocksCell } from './EditStocksCell'

interface IndividualActionsCellsProps {
  offer: ListOffersOfferResponseModel
  editionOfferLink: string
  editionStockLink: string
  isRestrictedAsAdmin: boolean
}

export const IndividualActionsCells = ({
  offer,
  editionOfferLink,
  editionStockLink,
  isRestrictedAsAdmin,
}: IndividualActionsCellsProps) => {
  const selectedOffererId = useSelector(selectCurrentOffererId)?.toString()
  const urlSearchFilters = useQuerySearchFilters()
  const { mutate } = useSWRConfig()
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const notification = useNotification()
  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogOpen(false)
  }, [])

  const apiFilters = computeIndividualApiFilters(
    urlSearchFilters,
    selectedOffererId?.toString(),
    isRestrictedAsAdmin
  )

  const onConfirmDeleteDraftOffer = async () => {
    try {
      await api.deleteDraftOffers({
        ids: [offer.id],
      })
      notification.success(computeDeletionSuccessMessage(1))
      logEvent(Events.DELETE_DRAFT_OFFER, {
        from: OFFER_FORM_NAVIGATION_IN.OFFERS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TRASH_ICON,
        offerId: offer.id,
        offerType: 'individual',
        isDraft: true,
      })
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
    } catch {
      notification.error(computeDeletionErrorMessage(1))
    }

    setIsConfirmDialogOpen(false)
  }

  return (
    <>
      <td
        role="cell"
        className={classNames(
          styles['offers-table-cell'],
          styles['actions-column']
        )}
      >
        <div className={styles['actions-column-container']}>
          <DropdownMenuWrapper title="Actions" triggerIcon={fullThreeDotsIcon}>
            <>
              <EditOfferCell editionOfferLink={editionOfferLink} />
              {offer.status === OFFER_STATUS_DRAFT ? (
                <DeleteDraftCell setIsConfirmDialogOpen={setIsConfirmDialogOpen} />
              ): (
                <EditStocksCell offer={offer} editionStockLink={editionStockLink} />
              )}
            </>
          </DropdownMenuWrapper>
        </div>
      </td>
      <ConfirmDialog
        icon={strokeTrashIcon}
        cancelText="Annuler"
        confirmText="Supprimer ce brouillon"
        onCancel={closeDeleteDraftDialog}
        onConfirm={onConfirmDeleteDraftOffer}
        title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
        open={isConfirmDialogOpen}
      />
    </>
  )
}

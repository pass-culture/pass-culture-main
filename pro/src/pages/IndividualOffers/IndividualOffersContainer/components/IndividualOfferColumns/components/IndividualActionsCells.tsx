import { useCallback, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useHeadlineOfferContext } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'commons/core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'commons/core/Offers/constants'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { computeDeletionErrorMessage } from 'pages/IndividualOffers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from 'pages/IndividualOffers/utils/computeDeletionSuccessMessage'
import { computeIndividualApiFilters } from 'pages/IndividualOffers/utils/computeIndividualApiFilters'
import styles from 'styles/components/Cells.module.scss'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'

import { DeleteDraftCell } from './DeleteDraftCell'
import { EditOfferCell } from './EditOfferCell'
import { EditStocksCell } from './EditStocksCell'
import { HeadlineOfferCell } from './HeadlineOfferCell/HeadlineOfferCell'
import { HeadlineOfferImageDialogs } from './HeadlineOfferImageDialogs'

interface IndividualActionsCellsProps {
  offer: ListOffersOfferResponseModel
  editionOfferLink: string
  editionStockLink: string
}

export const IndividualActionsCells = ({
  offer,
  editionOfferLink,
  editionStockLink,
}: IndividualActionsCellsProps) => {
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const { storedFilters } = getStoredFilterConfig('individual')
  const { isHeadlineOfferAllowedForOfferer, upsertHeadlineOffer } =
    useHeadlineOfferContext()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const urlSearchFilters = useQuerySearchFilters()
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<SearchFiltersParams>)
      : {}),
  }

  const dropdownTriggerRef = useRef<HTMLButtonElement>(null)

  const { mutate } = useSWRConfig()
  const [isConfirmDialogDeleteDraftOpen, setIsConfirmDialogDeleteDraftOpen] =
    useState(false)
  const [
    isConfirmDialogReplaceHeadlineOfferOpen,
    setIsConfirmDialogReplaceHeadlineOfferOpen,
  ] = useState(false)
  const [
    isDialogForHeadlineOfferWithoutImageOpen,
    setIsDialogForHeadlineOfferWithoutImageOpen,
  ] = useState(false)
  const { logEvent } = useAnalytics()
  const notification = useNotification()

  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogDeleteDraftOpen(false)
  }, [])
  const closeReplaceHeadlineOfferDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogReplaceHeadlineOfferOpen(false)
  }, [])

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId?.toString()
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

    setIsConfirmDialogDeleteDraftOpen(false)
  }

  const onConfirmReplaceHeadlineOffer = async () => {
    await upsertHeadlineOffer({
      offerId: offer.id,
      context: { actionType: 'replace' },
    })
    setIsConfirmDialogReplaceHeadlineOfferOpen(false)
  }

  const isActive = offer.status === OfferStatus.ACTIVE
  const isDigital = offer.isDigital
  const isProduct = !!offer.productId
  const hasImage = !!offer.thumbUrl
  // If an offer without an image is product-based, it cannot become
  // a headline offer since product-based offers cannot have their images
  // updated & headline offers without images are prohibited.
  const isNotAProductWithoutImage = !isProduct || hasImage

  const isHeadlineActionDisplayed =
    isHeadlineOfferAllowedForOfferer &&
    isActive &&
    !isDigital &&
    isNotAProductWithoutImage

  return (
    <>
      <div className={styles['actions-column']}>
        <div className={styles['actions-column-container']}>
          <DropdownMenuWrapper
            title="Voir les actions"
            triggerIcon={fullThreeDotsIcon}
            triggerTooltip
            dropdownTriggerRef={dropdownTriggerRef}
          >
            <>
              <EditOfferCell editionOfferLink={editionOfferLink} />
              {offer.status === OFFER_STATUS_DRAFT ? (
                <DeleteDraftCell
                  setIsConfirmDialogOpen={setIsConfirmDialogDeleteDraftOpen}
                />
              ) : (
                <EditStocksCell
                  offer={offer}
                  editionStockLink={editionStockLink}
                />
              )}{' '}
              {isHeadlineActionDisplayed && (
                <HeadlineOfferCell
                  offer={offer}
                  setIsConfirmReplacementDialogOpen={
                    setIsConfirmDialogReplaceHeadlineOfferOpen
                  }
                  setIsOfferWithoutImageDialogOpen={
                    setIsDialogForHeadlineOfferWithoutImageOpen
                  }
                />
              )}
            </>
          </DropdownMenuWrapper>
        </div>
      </div>
      <ConfirmDialog
        icon={strokeTrashIcon}
        cancelText="Annuler"
        confirmText="Supprimer ce brouillon"
        onCancel={closeDeleteDraftDialog}
        onConfirm={onConfirmDeleteDraftOffer}
        title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
        open={isConfirmDialogDeleteDraftOpen}
        refToFocusOnClose={dropdownTriggerRef}
      />
      <ConfirmDialog
        icon={strokeStarIcon}
        cancelText="Annuler"
        confirmText="Confirmer"
        onCancel={closeReplaceHeadlineOfferDialog}
        onConfirm={onConfirmReplaceHeadlineOffer}
        title={
          'Vous êtes sur le point de remplacer votre offre à la une par une nouvelle offre.'
        }
        open={isConfirmDialogReplaceHeadlineOfferOpen}
        refToFocusOnClose={dropdownTriggerRef}
      />
      <HeadlineOfferImageDialogs
        offer={offer}
        isFirstDialogOpen={isDialogForHeadlineOfferWithoutImageOpen}
        setIsFirstDialogOpen={setIsDialogForHeadlineOfferWithoutImageOpen}
      />
    </>
  )
}

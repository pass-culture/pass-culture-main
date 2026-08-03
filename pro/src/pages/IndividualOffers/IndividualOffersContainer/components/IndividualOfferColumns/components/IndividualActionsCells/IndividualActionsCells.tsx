import { getOfferEnhancementCardsVisibility } from 'commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { OfferRecommendationDialogBuilder } from 'components/IndividualOfferLayout/components/OfferRecommendationCard/OfferRecommendationDialogBuilder'
import { Button } from 'design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from 'design-system/Button/types'
import { useCallback, useRef, useState } from 'react'
import { Link } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { type ListOffersOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  EngagementEvents,
  Events,
  INDIVIDUAL_OFFERS_NAVIGATION_SOURCE,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from '@/commons/core/FirebaseEvents/constants'
import { useQuerySearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import penIcon from '@/icons/full-edit.svg'
import fullMessageIcon from '@/icons/full-message.svg'
import fullStarIcon from '@/icons/full-star.svg'
import fullStockIcon from '@/icons/full-stock.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeMessageIcon from '@/icons/stroke-message.svg'
import strokeStarIcon from '@/icons/stroke-star.svg'
import strokeTrashIcon from '@/icons/stroke-trash.svg'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'
import { computeDeletionErrorMessage } from '@/pages/IndividualOffers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from '@/pages/IndividualOffers/utils/computeDeletionSuccessMessage'
import { computeIndividualApiFilters } from '@/pages/IndividualOffers/utils/computeIndividualApiFilters'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

import { HeadlineOfferCell } from '../HeadlineOfferCell/HeadlineOfferCell'
import { HeadlineOfferImageDialogs } from '../HeadlineOfferImageDialogs'
import styles from './IndividualActionsCells.module.scss'

interface IndividualActionsCellsProps {
  offer: ListOffersOfferResponseModel
  editionOfferLink: string
  editionStockLink: string
  isHeadline: boolean
}

export const IndividualActionsCells = ({
  offer,
  editionOfferLink,
  editionStockLink,
  isHeadline,
}: IndividualActionsCellsProps) => {
  const { storedFilters } = useStoredFilterConfig('individual')
  const { headlineOffer, upsertHeadlineOffer, removeHeadlineOffer } =
    useHeadlineOfferContext()
  const urlSearchFilters = useQuerySearchFilters()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<IndividualOffersFilters>),
    venueId: selectedPartnerVenue.id,
  }
  const isNewProAdviceAccess = useActiveFeature('WIP_NEW_PRO_ADVICE_ACCESS')

  const dropdownTriggerRef = useRef<HTMLButtonElement>(null)
  const headlineButtonTriggerRef = useRef<HTMLButtonElement>(null)

  const { mutate } = useSWRConfig()
  const [isConfirmDialogDeleteDraftOpen, setIsConfirmDialogDeleteDraftOpen] =
    useState(false)
  const [isProAdviceOpen, setIsProAdviceOpen] = useState(false)

  const [
    isConfirmDialogReplaceHeadlineOfferOpen,
    setIsConfirmDialogReplaceHeadlineOfferOpen,
  ] = useState(false)
  const [
    isDialogForHeadlineOfferWithoutImageOpen,
    setIsDialogForHeadlineOfferWithoutImageOpen,
  ] = useState(false)
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()

  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogDeleteDraftOpen(false)
  }, [])
  const closeReplaceHeadlineOfferDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogReplaceHeadlineOfferOpen(false)
  }, [])

  const { shouldDisplayRecommendationCard, shouldDisplayHeadlineCard } =
    getOfferEnhancementCardsVisibility(offer)

  const apiFilters = computeIndividualApiFilters({
    finalSearchFilters,
    selectedVenueId: selectedPartnerVenue.id,
  })

  const onConfirmDeleteDraftOffer = async () => {
    try {
      await api.deleteDraftOffers({
        body: {
          ids: [offer.id],
        },
      })
      snackBar.success(computeDeletionSuccessMessage(1))
      logEvent(Events.DELETE_DRAFT_OFFER, {
        used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TRASH_ICON,
        offerId: offer.id,
        offerType: 'individual',
        isDraft: true,
      })
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
    } catch {
      snackBar.error(computeDeletionErrorMessage(1))
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

  async function onClickAddHeadlineOffer() {
    if (!shouldDisplayHeadlineCard) {
      snackBar.error(
        'Seules les offres au statut « Publié » peuvent être mises à la une.'
      )
      return
    }
    if (isHeadline) {
      await removeHeadlineOffer({ offerId: offer.id })
    } else if (offer.thumbUrl) {
      if (headlineOffer?.id) {
        setIsConfirmDialogReplaceHeadlineOfferOpen(true)
      } else {
        await upsertHeadlineOffer({
          offerId: offer.id,
          context: { actionType: 'add' },
        })
      }
    } else {
      setIsDialogForHeadlineOfferWithoutImageOpen(true)
    }
  }

  function onClickAddProAdvice() {
    if (!shouldDisplayRecommendationCard) {
      let errorMessage =
        'Votre offre doit être publiée pour faire cette action.'
      if (offer.status === OfferStatus.REJECTED) {
        errorMessage =
          "Offre non-conforme : aucune modification n'est possible dans ce cas. Veuillez créer une nouvelle offre."
      } else if (offer.status === OfferStatus.PENDING) {
        errorMessage =
          "Offre en cours de vérification : aucune modification n'est possible durant la vérification d’éligibilité."
      }
      snackBar.error(errorMessage)
    } else {
      logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
        offerId: offer.id,
        action: offer.hasProAdvice ? 'edited' : 'started',
      })
      setIsProAdviceOpen(true)
    }
  }

  const isActive = offer.status === OfferStatus.ACTIVE
  const isProduct = !!offer.productId
  const hasImage = !!offer.thumbUrl
  // If an offer without an image is product-based, it cannot become
  // a headline offer since product-based offers cannot have their images
  // updated & headline offers without images are prohibited.
  const isNotAProductWithoutImage = !isProduct || hasImage

  const isHeadlineActionDisplayed =
    !isNewProAdviceAccess && isActive && isNotAProductWithoutImage

  const logOfferNavigation = (source: INDIVIDUAL_OFFERS_NAVIGATION_SOURCE) => {
    logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      used: source,
      offerId: offer.id,
    })
  }

  return (
    <>
      <div className={styles['actions-column']}>
        {isNewProAdviceAccess && (
          <>
            <Button
              color={isHeadline ? ButtonColor.BRAND : ButtonColor.NEUTRAL}
              variant={ButtonVariant.SECONDARY}
              size={ButtonSize.SMALL}
              icon={
                isHeadline && shouldDisplayHeadlineCard
                  ? fullStarIcon
                  : strokeStarIcon
              }
              onClick={onClickAddHeadlineOffer}
              tooltip={
                isHeadline ? 'Ne plus mettre à la une' : 'Mettre à la une'
              }
              ref={headlineButtonTriggerRef}
            />

            <OfferRecommendationDialogBuilder
              onOpenChange={() => {
                if (shouldDisplayRecommendationCard) {
                  setIsProAdviceOpen(!isProAdviceOpen)
                }
              }}
              offerId={offer.id}
              isOpen={isProAdviceOpen}
              proAdvice={null}
              onSubmit={async () => {
                await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
                setIsProAdviceOpen(false)
              }}
              submitLabel={'Enregistrer la recommandation'}
              loadAdviceFromOffer={offer.hasProAdvice}
            >
              <Button
                color={
                  offer.hasProAdvice ? ButtonColor.BRAND : ButtonColor.NEUTRAL
                }
                variant={ButtonVariant.SECONDARY}
                size={ButtonSize.SMALL}
                icon={
                  offer.hasProAdvice && shouldDisplayRecommendationCard
                    ? fullMessageIcon
                    : strokeMessageIcon
                }
                onClick={onClickAddProAdvice}
                tooltip={
                  offer.hasProAdvice
                    ? 'Modifier la recommandation'
                    : 'Recommander'
                }
              />
            </OfferRecommendationDialogBuilder>
          </>
        )}
        <Dropdown
          title="Voir les actions"
          triggerTooltip
          dropdownTriggerRef={dropdownTriggerRef}
        >
          <DropdownItem icon={penIcon}>
            <Link
              to={editionOfferLink}
              onClick={() =>
                logOfferNavigation(
                  INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.ACTIONS_MENU_VIEW_OFFER
                )
              }
            >
              Voir l’offre
            </Link>
          </DropdownItem>
          {offer.status === OfferStatus.DRAFT ? (
            <DropdownItem
              onSelect={() =>
                setIsConfirmDialogDeleteDraftOpen(
                  !isConfirmDialogDeleteDraftOpen
                )
              }
              title="Supprimer l’offre"
              icon={fullTrashIcon}
            />
          ) : (
            <DropdownItem icon={fullStockIcon}>
              <Link
                to={editionStockLink}
                onClick={() =>
                  logOfferNavigation(
                    INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.ACTIONS_MENU_EDIT_OFFER_STOCK
                  )
                }
              >
                {offer.isEvent ? `Dates et capacités` : `Stocks`}
              </Link>
            </DropdownItem>
          )}
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
        </Dropdown>
      </div>
      <ConfirmDialog
        icon={strokeTrashIcon}
        cancelText="Annuler"
        confirmText="Supprimer ce brouillon"
        onCancel={closeDeleteDraftDialog}
        onConfirm={onConfirmDeleteDraftOffer}
        title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
        open={isConfirmDialogDeleteDraftOpen}
        refToFocusOnClose={
          isNewProAdviceAccess ? headlineButtonTriggerRef : dropdownTriggerRef
        }
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
        refToFocusOnClose={
          isNewProAdviceAccess ? headlineButtonTriggerRef : dropdownTriggerRef
        }
      />
      <HeadlineOfferImageDialogs
        offerId={offer.id}
        isFirstDialogOpen={isDialogForHeadlineOfferWithoutImageOpen}
        setIsFirstDialogOpen={setIsDialogForHeadlineOfferWithoutImageOpen}
      />
    </>
  )
}

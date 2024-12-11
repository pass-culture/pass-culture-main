import cn from 'classnames'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferStatus,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  Events,
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
} from 'commons/core/FirebaseEvents/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from 'commons/core/OfferEducational/utils/createOfferFromTemplate'
import { duplicateBookableOffer } from 'commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferStockEditionURL } from 'commons/hooks/useOfferEditionURL'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { canArchiveCollectiveOfferFromSummary } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import { Step, Stepper } from 'components/Stepper/Stepper'
import fullArchiveIcon from 'icons/full-archive.svg'
import fullCopyIcon from 'icons/full-duplicate.svg'
import fullPlusIcon from 'icons/full-plus.svg'
import fullShowIcon from 'icons/full-show.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Divider } from 'ui-kit/Divider/Divider'
import { Tabs } from 'ui-kit/Tabs/Tabs'

import styles from './CollectiveOfferNavigation.module.scss'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
  PREVIEW = 'preview',
}

export interface CollectiveOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: number
  className?: string
  isTemplate: boolean
  requestId?: string | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferNavigation = ({
  activeStep,
  isCreatingOffer,
  isTemplate = false,
  isCompletingDraft = false,
  offerId = 0,
  className,
  requestId = null,
  offer,
}: CollectiveOfferNavigationProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { mutate } = useSWRConfig()

  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false)

  const previewLink = `/offre/${computeURLCollectiveOfferId(
    offerId,
    isTemplate
  )}/collectif${isTemplate ? '/vitrine' : ''}/apercu`

  const stockEditionUrl = useOfferStockEditionURL(true, offerId)
  const isEditingExistingOffer = !(isCreatingOffer || isCompletingDraft)

  const stepList: { [key in CollectiveOfferStep]?: Step } = {}

  const canEditOffer =
    offer?.status !== CollectiveOfferStatus.ARCHIVED &&
    location.pathname.includes('edition')

  const canPreviewOffer =
    (isCollectiveOffer(offer) &&
      offer.displayedStatus !== CollectiveOfferDisplayedStatus.ARCHIVED) ||
    !isCollectiveOffer(offer)

  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  if (isEditingExistingOffer) {
    if (!isTemplate && canEditOffer) {
      stepList[CollectiveOfferStep.DETAILS] = {
        id: CollectiveOfferStep.DETAILS,
        label: 'Détails de l’offre',
        url: `/offre/${offerId}/collectif/edition`,
      }
      stepList[CollectiveOfferStep.STOCKS] = {
        id: CollectiveOfferStep.STOCKS,
        label: 'Dates et prix',
        url: stockEditionUrl,
      }
      stepList[CollectiveOfferStep.VISIBILITY] = {
        id: CollectiveOfferStep.VISIBILITY,
        label: 'Établissement et enseignant',
        url: `/offre/${offerId}/collectif/visibilite/edition`,
      }
    }
  } else {
    //  Creating an offer
    stepList[CollectiveOfferStep.DETAILS] = {
      id: CollectiveOfferStep.DETAILS,
      label: 'Détails de l’offre',
    }
    if (!isTemplate) {
      //  These steps only exist for bookable offers
      stepList[CollectiveOfferStep.STOCKS] = {
        id: CollectiveOfferStep.STOCKS,
        label: 'Dates et prix',
      }

      stepList[CollectiveOfferStep.VISIBILITY] = {
        id: CollectiveOfferStep.VISIBILITY,
        label: 'Établissement et enseignant',
      }
    }
    stepList[CollectiveOfferStep.SUMMARY] = {
      id: CollectiveOfferStep.SUMMARY,
      label: 'Récapitulatif',
    }
    stepList[CollectiveOfferStep.PREVIEW] = {
      id: CollectiveOfferStep.PREVIEW,
      label: 'Aperçu',
    }
    stepList[CollectiveOfferStep.CONFIRMATION] = {
      id: CollectiveOfferStep.CONFIRMATION,
      label: 'Confirmation',
    }

    const hasOfferPassedDetailsStep = offer && offerId
    const hasOfferPassedStocksStep =
      hasOfferPassedDetailsStep &&
      (isCollectiveOfferTemplate(offer) || offer.collectiveStock)
    const hasOfferPassedVisibilityStep =
      hasOfferPassedStocksStep &&
      (isCollectiveOfferTemplate(offer) || offer.institution)

    if (hasOfferPassedDetailsStep) {
      //  The user can go back to the details page after it has been filled the first time
      stepList[CollectiveOfferStep.DETAILS].url = isTemplate
        ? `/offre/collectif/vitrine/${offerId}/creation`
        : `/offre/collectif/${offerId}/creation${requestIdUrl}`

      if (
        !isCollectiveOfferTemplate(offer) &&
        stepList[CollectiveOfferStep.STOCKS]
      ) {
        //  The stocks step is accessible when the details form has been filled and the offer is bookable
        stepList[CollectiveOfferStep.STOCKS].url =
          `/offre/${offerId}/collectif/stocks`
      }
    }

    if (hasOfferPassedStocksStep && stepList[CollectiveOfferStep.VISIBILITY]) {
      //  The visibility tab is only accessible when the stocks form has been filled
      stepList[CollectiveOfferStep.VISIBILITY].url =
        `/offre/${offerId}/collectif/visibilite`
    }

    if (hasOfferPassedVisibilityStep) {
      //  The summary tab is only accessible when the visibility form has been filled (or the offer is a template)
      stepList[CollectiveOfferStep.SUMMARY].url = isTemplate
        ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
        : `/offre/${offerId}/collectif/creation/recapitulatif`

      stepList[CollectiveOfferStep.PREVIEW].url = isTemplate
        ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
        : `/offre/${offerId}/collectif/creation/apercu`
    }
  }

  const steps = Object.values(stepList)
  const tabs = steps.map(({ id, label, url }) => ({
    key: id,
    label,
    url,
  }))

  const archiveOffer = async () => {
    if (!offerId) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      if (isTemplate) {
        await api.patchCollectiveOffersTemplateArchive({ ids: [offerId] })
      } else {
        await api.patchCollectiveOffersArchive({ ids: [offerId] })
      }

      if (isTemplate) {
        await mutate([GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offerId])
      } else {
        await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offerId])
      }
      setIsArchiveModalOpen(false)
      notify.success('Une offre a bien été archivée', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    } catch {
      notify.error('Une erreur est survenue lors de l’archivage de l’offre', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }

  const canArchiveOffer = areCollectiveNewStatusesEnabled
    ? offer &&
      isActionAllowedOnCollectiveOffer(
        offer,
        isTemplate
          ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
          : CollectiveOfferAllowedAction.CAN_ARCHIVE
      )
    : offer && canArchiveCollectiveOfferFromSummary(offer)

  const canDuplicateOffer = offer
    ? areCollectiveNewStatusesEnabled
      ? isActionAllowedOnCollectiveOffer(
          offer,
          CollectiveOfferAllowedAction.CAN_DUPLICATE
        )
      : !isTemplate
    : false

  const canCreateBookableOffer = offer
    ? areCollectiveNewStatusesEnabled
      ? isActionAllowedOnCollectiveOffer(
          offer,
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
        )
      : isTemplate &&
        offer.displayedStatus !== CollectiveOfferDisplayedStatus.PENDING
    : false

  return isEditingExistingOffer ? (
    <>
      <div className={styles['duplicate-offer']}>
        {canPreviewOffer && (
          <ButtonLink to={previewLink} icon={fullShowIcon}>
            Aperçu dans ADAGE
          </ButtonLink>
        )}

        {canArchiveOffer && (
          <Button
            onClick={() => setIsArchiveModalOpen(true)}
            icon={fullArchiveIcon}
            variant={ButtonVariant.TERNARY}
          >
            Archiver
          </Button>
        )}

        {canDuplicateOffer && (
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullCopyIcon}
            onClick={async () => {
              logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
                from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_RECAP,
                offererId: selectedOffererId?.toString(),
                offerId,
                offerStatus: offer?.displayedStatus,
                offerType: 'collective',
              })
              await duplicateBookableOffer(navigate, notify, offerId)
            }}
          >
            Dupliquer
          </Button>
        )}

        {canCreateBookableOffer && (
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullPlusIcon}
            onClick={() => {
              if (isTemplate) {
                logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                  from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_RECAP,
                  offererId: selectedOffererId?.toString(),
                  offerId,
                  offerType: 'collective',
                  offerStatus: offer?.displayedStatus,
                })
                // eslint-disable-next-line @typescript-eslint/no-floating-promises
                createOfferFromTemplate(
                  navigate,
                  notify,
                  offerId,
                  undefined,
                  isMarseilleActive
                )
              }
            }}
          >
            Créer une offre réservable
          </Button>
        )}
      </div>
      <Divider />
      {tabs.length > 0 && (
        <Tabs
          tabs={tabs}
          selectedKey={activeStep}
          className={cn(styles['tabs'], {
            [styles['tabs-active']]: [
              CollectiveOfferStep.DETAILS,
              CollectiveOfferStep.STOCKS,
              CollectiveOfferStep.VISIBILITY,
            ].includes(activeStep),
          })}
        />
      )}
      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveModalOpen(false)}
        onValidate={archiveOffer}
        offer={offer}
        isDialogOpen={isArchiveModalOpen}
      />
    </>
  ) : (
    <Stepper activeStep={activeStep} className={className} steps={steps} />
  )
}

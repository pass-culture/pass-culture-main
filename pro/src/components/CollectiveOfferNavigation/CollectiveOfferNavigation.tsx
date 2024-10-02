import cn from 'classnames'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferStatus,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { Step, Stepper } from 'components/Stepper/Stepper'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import { useOfferStockEditionURL } from 'hooks/useOfferEditionURL'
import fullArchiveIcon from 'icons/full-archive.svg'
import fullMoreIcon from 'icons/full-more.svg'
import fullShowIcon from 'icons/full-show.svg'
import { selectCurrentOffererId } from 'store/user/selectors'
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
  isArchivable?: boolean | null
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
  isArchivable,
  offer,
}: CollectiveOfferNavigationProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')
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
    } catch (error) {
      notify.error('Une erreur est survenue lors de l’archivage de l’offre', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }

  return isEditingExistingOffer ? (
    <>
      <div className={styles['duplicate-offer']}>
        {canPreviewOffer && (
          <ButtonLink to={previewLink} icon={fullShowIcon}>
            Aperçu dans ADAGE
          </ButtonLink>
        )}

        {isArchivable && (
          <Button
            onClick={() => setIsArchiveModalOpen(true)}
            icon={fullArchiveIcon}
            variant={ButtonVariant.TERNARY}
          >
            Archiver
          </Button>
        )}

        {isTemplate && (
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullMoreIcon}
            onClick={() => {
              logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
                offererId: selectedOffererId?.toString(),
                offerId,
                offerType: 'collective',
              })
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              createOfferFromTemplate(
                navigate,
                notify,
                offerId,
                undefined,
                isMarseilleActive
              )
            }}
          >
            Créer une offre réservable
          </Button>
        )}
      </div>
      <Divider />
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
      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveModalOpen(false)}
        onValidate={archiveOffer}
        offerId={offerId}
        isDialogOpen={isArchiveModalOpen}
      />
    </>
  ) : (
    <Stepper activeStep={activeStep} className={className} steps={steps} />
  )
}

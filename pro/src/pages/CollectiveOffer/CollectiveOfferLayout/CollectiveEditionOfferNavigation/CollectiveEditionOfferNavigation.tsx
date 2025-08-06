import cn from 'classnames'
import { useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from '@/commons/core/Notification/constants'
import { isCollectiveOffer } from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import fullArchiveIcon from '@/icons/full-archive.svg'
import fullCopyIcon from '@/icons/full-duplicate.svg'
import fullPlusIcon from '@/icons/full-plus.svg'
import fullShowIcon from '@/icons/full-show.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { NavLinkItem, NavLinkItems } from '@/ui-kit/NavLinkItems/NavLinkItems'

import { CollectiveOfferStep } from '../CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import styles from './CollectiveEditionOfferNavigation.module.scss'

export interface CollectiveEditionOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isTemplate: boolean
  offerId?: number
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveEditionOfferNavigation = ({
  activeStep,
  isTemplate = false,
  offerId = 0,
  offer,
}: CollectiveEditionOfferNavigationProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false)

  const id = computeURLCollectiveOfferId(offerId, Boolean(isTemplate))

  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const adagePreviewButtonRef = useRef<HTMLAnchorElement>(null)

  const archiveOffer = async () => {
    if (!offerId) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      if (isTemplate) {
        await api.patchCollectiveOffersTemplateArchive({ ids: [offerId] })
        await mutate([GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offerId])
      } else {
        await api.patchCollectiveOffersArchive({ ids: [offerId] })
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

  const canEditOffer =
    offer?.displayedStatus !== CollectiveOfferDisplayedStatus.ARCHIVED &&
    location.pathname.includes('edition')

  const canPreviewOffer =
    (isCollectiveOffer(offer) &&
      offer.displayedStatus !== CollectiveOfferDisplayedStatus.ARCHIVED) ||
    !isCollectiveOffer(offer)

  const canArchiveOffer =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      isTemplate
        ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
        : CollectiveOfferAllowedAction.CAN_ARCHIVE
    )

  const canDuplicateOffer =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferAllowedAction.CAN_DUPLICATE
    )

  const canCreateBookableOffer =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
    )

  const tabs: NavLinkItem[] = [
    {
      key: CollectiveOfferStep.DETAILS,
      label: 'Détails de l’offre',
      url: `/offre/${offerId}/collectif/edition`,
    },
    {
      key: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
      url: `/offre/${offerId}/collectif/stocks/edition`,
    },
    {
      key: CollectiveOfferStep.VISIBILITY,
      label: 'Établissement et enseignant',
      url: `/offre/${offerId}/collectif/visibilite/edition`,
    },
  ]

  return (
    <>
      <div className={styles['duplicate-offer']}>
        {canPreviewOffer && (
          <ButtonLink
            to={`/offre/${id}/collectif${isTemplate ? '/vitrine' : ''}/apercu`}
            icon={fullShowIcon}
            ref={adagePreviewButtonRef}
          >
            Aperçu dans ADAGE
          </ButtonLink>
        )}

        {canArchiveOffer && (
          <Button
            onClick={() => setIsArchiveModalOpen(true)}
            icon={fullArchiveIcon}
            variant={ButtonVariant.TERNARY}
            ref={archiveButtonRef}
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
                offerStatus: offer.displayedStatus,
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
                  offerStatus: offer.displayedStatus,
                })
                // eslint-disable-next-line @typescript-eslint/no-floating-promises
                createOfferFromTemplate(
                  navigate,
                  notify,
                  offerId,
                  isCollectiveOaActive,
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
      {!isTemplate && canEditOffer && (
        <NavLinkItems
          links={tabs}
          selectedKey={activeStep}
          navLabel="Sous menu - offre collective"
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
        refToFocusOnClose={
          archiveButtonRef.current ? archiveButtonRef : adagePreviewButtonRef
        }
      />
    </>
  )
}

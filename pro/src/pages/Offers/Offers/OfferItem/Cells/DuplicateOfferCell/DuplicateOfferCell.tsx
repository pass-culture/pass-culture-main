import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import useAnalytics from 'app/App/analytics/firebase'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import { createOfferFromBookableOffer } from 'core/OfferEducational/utils/createOfferFromBookableOffer'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import useActiveFeature from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import copyIcon from 'icons/full-duplicate.svg'
import fullPlusIcon from 'icons/full-plus.svg'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import { DuplicateOfferDialog } from './DuplicateOfferDialog/DuplicateOfferDialog'

export const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

export const DuplicateOfferCell = ({
  offerId,
  isShowcase,
}: {
  offerId: number
  isShowcase?: boolean | null
}) => {
  const navigate = useNavigate()
  const notify = useNotification()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const { logEvent } = useAnalytics()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const isLocalStorageAvailable = localStorageAvailable()
  const shouldDisplayModal =
    !isLocalStorageAvailable ||
    localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY) !== 'true'

  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const onDialogConfirm = async (shouldNotDisplayModalAgain: boolean) => {
    logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS_MODAL,
    })
    if (shouldNotDisplayModalAgain && isLocalStorageAvailable) {
      localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')
    }
    await createOfferFromTemplate(
      navigate,
      notify,
      offerId,
      undefined,
      isMarseilleActive
    )
  }

  const handleCreateOfferClick = async () => {
    if (isShowcase) {
      if (!shouldDisplayModal) {
        logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
          from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS,
        })
        await createOfferFromTemplate(
          navigate,
          notify,
          offerId,
          undefined,
          isMarseilleActive
        )
      }
      buttonRef.current?.blur()
      setIsModalOpen(true)
    } else {
      await createOfferFromBookableOffer(navigate, notify, offerId)
    }
  }

  return (
    <>
      <ListIconButton
        onClick={handleCreateOfferClick}
        icon={isShowcase ? fullPlusIcon : copyIcon}
        innerRef={buttonRef}
      >
        {isShowcase ? 'Créer une offre réservable' : 'Dupliquer'}
      </ListIconButton>
      {isModalOpen && shouldDisplayModal && (
        <DuplicateOfferDialog
          onCancel={() => setIsModalOpen(false)}
          onConfirm={onDialogConfirm}
        />
      )}
    </>
  )
}

import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import { createOfferFromTemplate } from 'core/OfferEducational'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ReactComponent as PlusIcon } from 'icons/ico-plus.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

import DuplicateOfferDialog from './DuplicateOfferDialog'

export const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

const DuplicateOfferCell = ({
  templateOfferId,
}: {
  templateOfferId: string
}) => {
  const navigate = useNavigate()
  const notify = useNotification()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const { logEvent } = useAnalytics()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const shouldDisplayModal =
    localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY) !== 'true'

  const onDialogConfirm = (shouldNotDisplayModalAgain: boolean) => {
    logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS_MODAL,
    })
    if (shouldNotDisplayModalAgain) {
      localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')
    }
    createOfferFromTemplate(navigate, notify, templateOfferId)
  }

  const handleCreateOfferClick = () => {
    if (!shouldDisplayModal) {
      logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
        from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS,
      })
      createOfferFromTemplate(navigate, notify, templateOfferId)
    }
    buttonRef.current?.blur()
    setIsModalOpen(true)
  }

  return (
    <>
      <ListIconButton
        onClick={handleCreateOfferClick}
        Icon={PlusIcon}
        innerRef={buttonRef}
        hasTooltip
      >
        Dupliquer
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
export default DuplicateOfferCell

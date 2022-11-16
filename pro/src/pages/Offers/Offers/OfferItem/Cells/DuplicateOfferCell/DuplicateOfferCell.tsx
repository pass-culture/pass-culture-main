import React, { useState } from 'react'
import { useHistory } from 'react-router'

import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  createOfferFromTemplate,
  oldCreateOfferFromTemplate,
} from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ReactComponent as PlusIcon } from 'icons/ico-plus.svg'
import { Button } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

import DuplicateOfferDialog from './DuplicateOfferDialog'

export const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

const DuplicateOfferCell = ({
  isTemplate,
  templateOfferId,
}: {
  isTemplate: boolean
  templateOfferId: string
}) => {
  const history = useHistory()
  const notify = useNotification()
  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )
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
    if (isSubtypeChosenAtCreation) {
      createOfferFromTemplate(history, notify, templateOfferId)
    } else {
      oldCreateOfferFromTemplate(history, templateOfferId)
    }
  }

  const handleCreateOfferClick = () => {
    if (!shouldDisplayModal) {
      logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
        from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS,
      })
      if (isSubtypeChosenAtCreation) {
        createOfferFromTemplate(history, notify, templateOfferId)
      } else {
        oldCreateOfferFromTemplate(history, templateOfferId)
      }
    }
    setIsModalOpen(true)
  }

  return (
    <>
      <td className={styles['duplicate-offer-column']}>
        {isTemplate ? (
          <Button
            variant={ButtonVariant.SECONDARY}
            className={styles['button']}
            onClick={handleCreateOfferClick}
            Icon={PlusIcon}
            iconPosition={IconPositionEnum.CENTER}
            hasTooltip
          >
            Créer une offre réservable pour un établissement
          </Button>
        ) : null}
        {isModalOpen && shouldDisplayModal && (
          <DuplicateOfferDialog
            onCancel={() => setIsModalOpen(false)}
            onConfirm={onDialogConfirm}
          />
        )}
      </td>
    </>
  )
}
export default DuplicateOfferCell

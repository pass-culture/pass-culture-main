import { useState } from 'react'

import { api } from '@/apiClient/api'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import {
  ensureSelectedAdminOfferer,
  ensureSelectedPartnerVenue,
} from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import { CloseVenueModal } from './CloseVenueModal/CloseVenueModal'
import { ConfirmVenueClosedModal } from './ConfirmVenueClosedModal/ConfirmVenueClosedModal'
import styles from './VenueManagement.module.scss'

const VenueManagement = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const selectedOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed
  const snackBar = useSnackBar()
  const { syncVenue } = useSyncVenueCache()
  const isLastOpenedVenue =
    selectedOfferer.managedVenues.filter(
      (venue) => !withVenueHelpers(venue).isClosed
    ).length === 1
  const [isCloseVenueModalOpen, setIsCloseVenueModalOpen] = useState(false)
  const [isConfirmVenueClosedModalOpen, setIsConfirmVenueClosedModalOpen] =
    useState(false)

  const onValidateModal = () => {
    setIsCloseVenueModalOpen(false)
    tryToCloseVenue()
  }

  const tryToCloseVenue = async () => {
    try {
      await api.closeVenue({
        path: { venue_id: Number(selectedPartnerVenue.id) },
      })

      await syncVenue(Number(selectedPartnerVenue.id))
      setIsConfirmVenueClosedModalOpen(true)
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

  return (
    <>
      <div className={styles['banner']}>
        <div className={styles['banner-container']}>
          <h2 className={styles['banner-title']}>Fermeture de la structure</h2>
          <p className={styles['banner-description']}>
            Toutes vos offres seront retirées du pass Culture.
          </p>
        </div>
        <Button
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.DANGER}
          disabled={isVenueClosed}
          label="Fermer la structure"
          onClick={() => setIsCloseVenueModalOpen(true)}
        />
      </div>

      <CloseVenueModal
        isLastOpenedVenue={isLastOpenedVenue}
        name={selectedPartnerVenue.name}
        siret={selectedPartnerVenue.siret}
        onCancel={() => setIsCloseVenueModalOpen(false)}
        isOpen={isCloseVenueModalOpen}
        onValidate={onValidateModal}
      />
      <ConfirmVenueClosedModal
        isPricingPoint={selectedPartnerVenue.isPricingPoint}
        onValidate={() => setIsConfirmVenueClosedModalOpen(false)}
        isOpen={isConfirmVenueClosedModalOpen}
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueManagement

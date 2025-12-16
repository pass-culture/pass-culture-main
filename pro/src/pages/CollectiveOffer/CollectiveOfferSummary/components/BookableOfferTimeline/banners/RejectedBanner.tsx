import { useNavigate } from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullDuplicateIcon from '@/icons/full-duplicate.svg'

import styles from '../BookableOfferTimeline.module.scss'

export const RejectedBanner = ({
  offerId,
  canDuplicate,
}: {
  offerId: number
  canDuplicate: boolean
}) => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const snackBar = useSnackBar()

  return (
    <div className={styles['callout']}>
      <Banner
        title="Informations"
        variant={BannerVariants.ERROR}
        description="Votre offre a été rejetée par notre équipe en charge du contrôle de conformité. Vous avez reçu un mail précisant les raisons de cette décision. Vous pouvez dupliquer cette offre et la corriger pour la publier et la soumettre à nouveau à notre équipe."
        actions={
          canDuplicate
            ? [
                {
                  label: "Dupliquer l'offre",
                  icon: fullDuplicateIcon,
                  type: 'button',
                  href: '',
                  onClick: async () => {
                    logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
                      from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_TIMELINE,
                      offererId: selectedOffererId?.toString(),
                      offerId,
                      offerStatus: CollectiveOfferDisplayedStatus.REJECTED,
                      offerType: 'collective',
                    })
                    await duplicateBookableOffer(navigate, snackBar, offerId)
                  },
                },
              ]
            : []
        }
      />
    </div>
  )
}

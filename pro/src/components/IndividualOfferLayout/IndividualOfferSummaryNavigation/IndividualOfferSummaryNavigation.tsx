import { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { NavLinkItems } from '@/ui-kit/NavLinkItems/NavLinkItems'

import { LabelBooking } from '../IndividualOfferNavigation/LabelBooking/LabelBooking'
import styles from './IndividualOfferSummaryNavigation.module.scss'

export function IndividualOfferSummaryNavigation({
  offer,
}: {
  offer: GetIndividualOfferResponseModel
}) {
  const activeStep = useActiveStep(
    Object.values(INDIVIDUAL_OFFER_WIZARD_STEP_IDS)
  )

  if (!offer.bookingsCount) {
    return
  }

  return (
    <NavLinkItems
      className={styles['links']}
      navLabel="Sous menu - offre individuelle"
      links={[
        {
          key: 'recapitulatif',
          label: 'Récapitulatif',
          url: getIndividualOfferUrl({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
            isOnboarding: false,
            offerId: offer.id,
          }),
        },
        {
          key: 'reservations',
          label: <LabelBooking bookingsCount={offer.bookingsCount} />,
          url: getIndividualOfferUrl({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
            isOnboarding: false,
            offerId: offer.id,
          }),
        },
      ]}
      selectedKey={activeStep}
    />
  )
}

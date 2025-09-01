import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getDelayToFrenchText } from '@/commons/utils/date'
import { SummaryContent } from '@/components/SummaryLayout/SummaryContent'
import {
  type Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from '@/components/SummaryLayout/SummaryLayout'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

import styles from './IndividualOfferSummaryPracticalInfosScreen.module.scss'

export type IndividualOfferSummaryPracticalInfosScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryPracticalInfosScreen({
  offer,
}: IndividualOfferSummaryPracticalInfosScreenProps) {
  const practicalInfoDescriptions: Description[] = []

  if (offer.withdrawalType) {
    practicalInfoDescriptions.push({
      title: 'Précisez la façon dont vous distribuerez les billets',
      text: OFFER_WITHDRAWAL_TYPE_LABELS[offer.withdrawalType],
    })
  }
  if (offer.withdrawalDelay) {
    practicalInfoDescriptions.push({
      title: 'Heure de retrait',
      text: `${getDelayToFrenchText(offer.withdrawalDelay)} avant le début de l’évènement`,
    })
  }
  practicalInfoDescriptions.push({
    title: 'Informations complémentaires',
    text: offer.withdrawalDetails || ' - ',
  })
  if (offer.bookingContact) {
    practicalInfoDescriptions.push({
      title: 'Email de contact',
      text: offer.bookingContact || ' - ',
    })
  }
  return (
    <SummaryLayout>
      <SummaryContent>
        <SummarySection
          title="Informations pratiques"
          editLink={getIndividualOfferUrl({
            offerId: offer.id,
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          aria-label="Modifier les détails de l’offre"
        >
          <div className={styles['withdrawal-block']}>
            <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
          </div>
          <SummarySubSection title="Lien de réservation externe en l’absence de crédit">
            <SummaryDescriptionList
              descriptions={[
                {
                  title: 'URL de votre site ou billetterie',
                  text: offer.externalTicketOfficeUrl || ' - ',
                },
              ]}
            />
          </SummarySubSection>
          <SummarySubSection title="Notification des réservations">
            <SummaryDescriptionList
              descriptions={[
                {
                  title: 'Email auquel envoyer les notifications',
                  text: offer.bookingEmail || ' - ',
                },
              ]}
            />
          </SummarySubSection>
        </SummarySection>
      </SummaryContent>
    </SummaryLayout>
  )
}

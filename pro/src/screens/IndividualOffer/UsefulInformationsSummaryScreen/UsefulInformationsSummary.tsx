import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import {
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'

import { humanizeDelay } from '../SummaryScreen/OfferSection/utils'

type DetailsSummaryScreenProps = {
  offer: GetIndividualOfferResponseModel
}

export function UsefulInformationsSummaryScreen({
  offer,
}: DetailsSummaryScreenProps) {
  const practicalInfoDescriptions: Description[] = []

  if (offer.withdrawalType) {
    practicalInfoDescriptions.push({
      title: 'Précisez la façon dont vous distribuerez les billets',
      text: OFFER_WITHDRAWAL_TYPE_LABELS[offer.withdrawalType],
    })
  }
  practicalInfoDescriptions.push({
    title: 'Informations de retrait',
    text: offer.withdrawalDetails || ' - ',
  })
  if (offer.withdrawalDelay) {
    practicalInfoDescriptions.push({
      title: 'Heure de retrait',
      text: `${humanizeDelay(offer.withdrawalDelay)} avant le début de l’évènement`,
    })
  }
  if (offer.bookingContact) {
    practicalInfoDescriptions.push({
      title: 'Email de contact',
      text: offer.bookingContact || ' - ',
    })
  }
  if (offer.venue.isVirtual) {
    practicalInfoDescriptions.push({
      title: 'URL d’accès à l’offre',
      text: offer.url || ' - ',
    })
  }
  return (
    <SummaryLayout>
      <SummaryContent>
        <SummarySection
          title="Informations pratiques"
          editLink={getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          aria-label="Modifier les détails de l’offre"
        >
          <SummarySubSection title="Retrait de l’offre">
            <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
          </SummarySubSection>
          <AccessibilitySummarySection
            accessibleItem={offer}
            accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
          />
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

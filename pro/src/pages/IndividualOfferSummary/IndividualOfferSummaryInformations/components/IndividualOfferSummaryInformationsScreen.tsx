import { computeAddressDisplayName } from 'repository/venuesService'

import { GetIndividualOfferWithAddressResponseModel } from '@/apiClient//v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getDelayToFrenchText } from '@/commons/utils/date'
import { AccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { SummaryContent } from '@/components/SummaryLayout/SummaryContent'
import {
  Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from '@/components/SummaryLayout/SummaryLayout'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

type DetailsSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryInformationsScreen({
  offer,
}: Readonly<DetailsSummaryScreenProps>) {
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
      text: `${getDelayToFrenchText(offer.withdrawalDelay)} avant le début de l’évènement`,
    })
  }
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
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          aria-label="Modifier les détails de l’offre"
        >
          {!offer.isDigital && (
            <SummarySubSection title="Localisation de l’offre">
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'Intitulé',
                    text: offer.address?.label || '-',
                  },
                  {
                    title: 'Adresse',
                    text: offer.address
                      ? computeAddressDisplayName(offer.address, false)
                      : '-',
                  },
                ]}
              />
            </SummarySubSection>
          )}
          <SummarySubSection title="Retrait de l’offre">
            <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
          </SummarySubSection>
          <AccessibilitySummarySection
            accessibleItem={offer}
            accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
          />
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

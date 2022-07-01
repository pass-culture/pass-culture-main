import { AccessibilityLabel, AccessiblityLabelEnum } from 'ui-kit'

import { OFFER_WITHDRAWAL_TYPE_LABELS } from 'core/Offers'
import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { WithdrawalTypeEnum } from 'apiClient/v1'
import humanizeDelay from './utils'
import styles from './OfferSummary.module.scss'

export interface IOfferSectionProps {
  id: string
  nonHumanizedId: number
  name: string
  description: string
  categoryName: string
  subCategoryName: string

  musicTypeName?: string
  musicSubTypeName?: string
  showTypeName?: string
  showSubTypeName?: string

  visualDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
  noDisabilityCompliant: boolean

  isDuo: boolean
  author: string
  stageDirector: string
  speaker: string
  visa: string
  performer: string
  isbn: string
  durationMinutes: string
  url: string

  venueName: string
  venuePublicName: string
  offererName: string
  bookingEmail: string
  withdrawalDetails: string
  withdrawalType: WithdrawalTypeEnum | null
  withdrawalDelay: number | null
}

interface IOfferSummaryProps {
  offer: IOfferSectionProps
  isCreation: boolean
}

const OfferSummary = ({
  isCreation,
  offer,
}: IOfferSummaryProps): JSX.Element => {
  const editLink = isCreation
    ? `/offre/${offer.id}/individuel/creation`
    : `/offre/${offer.id}/individuel/edition`
  return (
    <SummaryLayout.Section title="Détails de l'offre" editLink={editLink}>
      <SummaryLayout.SubSection title="Type d'offre">
        <SummaryLayout.Row title="Catégorie" description={offer.categoryName} />
        <SummaryLayout.Row
          title="Sous-catégorie"
          description={offer.subCategoryName}
        />

        {offer.musicTypeName && (
          <SummaryLayout.Row
            title="Genre musical"
            description={offer.musicTypeName}
          />
        )}
        {offer.musicSubTypeName && (
          <SummaryLayout.Row
            title="Sous-genre"
            description={offer.musicSubTypeName}
          />
        )}
        {offer.showTypeName && (
          <SummaryLayout.Row
            title="Type de spéctacle"
            description={offer.showTypeName}
          />
        )}
        {offer.showSubTypeName && (
          <SummaryLayout.Row
            title="Sous-type"
            description={offer.showSubTypeName}
          />
        )}
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations artistiques">
        <SummaryLayout.Row title="Titre de l'offre" description={offer.name} />
        <SummaryLayout.Row
          title="Description"
          description={offer.description || ' - '}
        />

        {offer.speaker && (
          <SummaryLayout.Row title="Intervenant" description={offer.speaker} />
        )}
        {offer.author && (
          <SummaryLayout.Row title="Auteur" description={offer.author} />
        )}
        {offer.speaker && (
          <SummaryLayout.Row
            title="Visa d’exploitation"
            description={offer.visa}
          />
        )}
        {offer.speaker && (
          <SummaryLayout.Row title="ISBN" description={offer.isbn} />
        )}
        {offer.stageDirector && (
          <SummaryLayout.Row
            title="Metteur en scène"
            description={offer.stageDirector}
          />
        )}
        {offer.performer && (
          <SummaryLayout.Row title="Interprète" description={offer.performer} />
        )}
        <SummaryLayout.Row
          title="Durée"
          description={
            offer.durationMinutes ? `${offer.durationMinutes} min` : '-'
          }
        />
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations pratiques">
        <SummaryLayout.Row title="Structure" description={offer.offererName} />
        <SummaryLayout.Row
          title="Lieu"
          description={offer.venuePublicName || offer.venueName}
        />
        {offer.withdrawalType && (
          <SummaryLayout.Row
            title="Comment les billets, places seront-ils transmis ?"
            description={OFFER_WITHDRAWAL_TYPE_LABELS[offer.withdrawalType]}
          />
        )}

        {offer.withdrawalDelay && (
          <SummaryLayout.Row
            title="Heure de retrait"
            description={humanizeDelay(offer.withdrawalDelay)}
          />
        )}

        <SummaryLayout.Row
          title="Informations de retrait"
          description={offer.withdrawalDetails || ' - '}
        />
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Accessibilité">
        {offer.noDisabilityCompliant && (
          <SummaryLayout.Row description="Non accessible" />
        )}
        {offer.visualDisabilityCompliant && (
          <AccessibilityLabel
            className={styles['accessibility-row']}
            name={AccessiblityLabelEnum.Visual}
          />
        )}
        {offer.mentalDisabilityCompliant && (
          <AccessibilityLabel
            className={styles['accessibility-row']}
            name={AccessiblityLabelEnum.Mental}
          />
        )}
        {offer.motorDisabilityCompliant && (
          <AccessibilityLabel
            className={styles['accessibility-row']}
            name={AccessiblityLabelEnum.Motor}
          />
        )}
        {offer.audioDisabilityCompliant && (
          <AccessibilityLabel
            className={styles['accessibility-row']}
            name={AccessiblityLabelEnum.Audio}
          />
        )}
      </SummaryLayout.SubSection>

      {offer.isDuo === true && (
        <SummaryLayout.SubSection title="Autres caractèristiques">
          <SummaryLayout.Row description='Accepter les réservations "Duo"' />
        </SummaryLayout.SubSection>
      )}

      {offer.url && (
        <SummaryLayout.SubSection title="Lien pour grand public">
          <SummaryLayout.Row description={offer.url} />
        </SummaryLayout.SubSection>
      )}

      <SummaryLayout.SubSection title="Notifications des réservations">
        {offer.bookingEmail ? (
          <SummaryLayout.Row description={offer.bookingEmail} />
        ) : (
          ' - '
        )}
      </SummaryLayout.SubSection>
    </SummaryLayout.Section>
  )
}

export default OfferSummary

import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { SelectOption } from 'custom_types/form'
import { getInterventionAreaLabels } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea'

interface CollectiveDataEditionReadOnlyProps {
  venue: GetVenueResponseModel
  culturalPartners: SelectOption[]
}

export const CollectiveDataEditionReadOnly = ({
  venue,
  culturalPartners,
}: CollectiveDataEditionReadOnlyProps) => {
  return (
    <SummarySection
      title="Vos informations pour les enseignants"
      editLink={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif/edition`}
    >
      <SummarySubSection title="Présentation pour les enseignants">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Démarche d’éducation artistique et culturelle',
              text: venue.collectiveDescription ?? 'Non renseignée',
            },
            {
              title: 'Public cible',
              text: venue.collectiveStudents?.join(', ') ?? 'Non renseignée', // TODO formatting
            },
            {
              title: 'URL de votre site web',
              text: venue.collectiveWebsite ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Informations du lieu">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Domaine artistique et culturel',
              text:
                venue.collectiveDomains.length > 0
                  ? venue.collectiveDomains
                      .map((domain) => domain.name)
                      .join(', ')
                  : 'Non renseigné',
            },
            {
              title: 'Zone de mobilité',
              text: venue.collectiveInterventionArea
                ? getInterventionAreaLabels(venue.collectiveInterventionArea)
                : 'Non renseignée',
            },
            {
              title: 'Statut',
              text: venue.collectiveLegalStatus?.name ?? 'Non renseigné',
            },
            {
              title: 'Réseaux partenaires EAC',
              text:
                venue.collectiveNetwork
                  ?.map(
                    (network) =>
                      culturalPartners.find(
                        (partner) => partner.value === network
                      )?.label
                  )
                  .join(', ') ?? 'Non renseigné',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Contact">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: venue.collectivePhone ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: venue.collectiveEmail ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}

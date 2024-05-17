import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import useActiveFeature from 'hooks/useActiveFeature'
import { OpeningHoursReadOnly } from 'pages/VenueEdition/OpeningHoursReadOnly/OpeningHoursReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isOpeningHoursEnabled = useActiveFeature('WIP_OPENING_HOURS')
  const isAccesLibreEnabled = useActiveFeature('WIP_ACCESLIBRE')

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/edition`}
    >
      <SummarySubSection title="À propos de votre activité">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Description',
              text: venue.description ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      {isOpeningHoursEnabled && venue.isPermanent && (
        <OpeningHoursReadOnly openingHours={venue.openingHours} />
      )}

      <SummarySubSection title="Informations de contact">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: venue.contact?.phoneNumber ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: venue.contact?.email ?? 'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text: venue.contact?.website ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      {!(isAccesLibreEnabled && venue.externalAccessibilityData) && (
        <AccessibilitySummarySection
          callout={
            isAccesLibreEnabled && venue.isPermanent ? (
              <Callout
                links={[
                  {
                    href: 'https://acceslibre.beta.gouv.fr/',
                    label: 'Aller sur acceslibre.beta.gouv.fr ',
                    isExternal: true,
                  },
                ]}
                variant={CalloutVariant.INFO}
              >
                Renseignez facilement les modalités d’accessibilité de votre
                établissement sur la plateforme collaborative
                acceslibre.beta.gouv.fr
              </Callout>
            ) : null
          }
          accessibleItem={venue}
          accessibleWording="Votre établissement est accessible aux publics en situation de handicap :"
        />
      )}
    </SummarySection>
  )
}

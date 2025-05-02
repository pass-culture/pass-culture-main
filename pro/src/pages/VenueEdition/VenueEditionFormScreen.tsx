import { useLocation } from 'react-router'

import { GetVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { PartnerPageIndividualSection } from 'pages/Homepage/components/Offerers/components/PartnerPages/components/PartnerPageIndividualSection'
import { Callout } from 'ui-kit/Callout/Callout'

import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

interface VenueEditionProps {
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  venue,
}: VenueEditionProps): JSX.Element => {
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')
  const shouldDisplayPartnerPageSection = !isOpenToPublicEnabled

  const location = useLocation()

  if (venue.isVirtual) {
    return (
      <Callout title="Cette structure vous permet uniquement de créer des offres numériques, elle n’est pas visible sur l’application pass Culture.">
        Vous n’avez pas d’informations à remplir à destination du grand public.
        Si vous souhaitez modifier d’autres informations, vous pouvez vous
        rendre dans la page "Paramètres généraux".
      </Callout>
    )
  }

  return (
    <>
      {venue.isPermanent && (
        <>
          <div className={styles['page-status']}>
            <Callout>
              Les informations que vous renseignez ci-dessous sont affichées
              dans votre page partenaire, visible sur l’application pass Culture
            </Callout>
            {shouldDisplayPartnerPageSection && <PartnerPageIndividualSection
              venueId={venue.id}
              venueName={venue.name}
              offererId={venue.managingOfferer.id}
              isVisibleInApp={Boolean(venue.isVisibleInApp)}
            />}
          </div>
          {shouldDisplayPartnerPageSection && <hr className={styles['separator']} />}
        </>
      )}

      {location.pathname.includes('/edition') ? (
        <VenueEditionForm venue={venue} />
      ) : (
        <VenueEditionReadOnly venue={venue} />
      )}
    </>
  )
}

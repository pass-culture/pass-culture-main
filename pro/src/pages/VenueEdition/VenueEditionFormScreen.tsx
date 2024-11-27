import { Route, Routes } from 'react-router-dom'

import { GetVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { Callout } from 'components/Callout/Callout'
import { PartnerPageIndividualSection } from 'pages/Homepage/components/Offerers/components/PartnerPages/components/PartnerPageIndividualSection'

import { AccesLibreSection } from './AccesLibreSection/AccesLibreSection'
import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

interface VenueEditionProps {
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  venue,
}: VenueEditionProps): JSX.Element => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  if (venue.isVirtual) {
    return (
      <Callout
        title={`${isOfferAddressEnabled ? 'Cette structure' : 'Ce lieu'} vous permet uniquement de créer des offres numériques, ${isOfferAddressEnabled ? 'elle' : 'il'} n’est pas visible sur l’application pass Culture.`}
      >
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
            <PartnerPageIndividualSection
              venueId={venue.id}
              venueName={venue.name}
              offererId={venue.managingOfferer.id}
              isVisibleInApp={Boolean(venue.isVisibleInApp)}
            />
          </div>

          <hr className={styles['separator']} />
        </>
      )}

      <Routes>
        <Route path="" element={<VenueEditionReadOnly venue={venue} />} />
        <Route path="/edition" element={<VenueEditionForm venue={venue} />} />
      </Routes>

      {venue.externalAccessibilityData && (
        <>
          <hr className={styles['separator']} />
          <AccesLibreSection venue={venue} />
        </>
      )}
    </>
  )
}

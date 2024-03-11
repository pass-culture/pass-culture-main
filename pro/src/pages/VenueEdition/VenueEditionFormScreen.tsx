import { Route, Routes } from 'react-router-dom'

import { GetVenueResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { PartnerPageIndividualSection } from 'pages/Home/Offerers/PartnerPageIndividualSection'

import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

interface VenueEditionProps {
  venue: GetVenueResponseModel
  reloadVenueData: () => Promise<void>
}

export const VenueEditionFormScreen = ({
  venue,
  reloadVenueData,
}: VenueEditionProps): JSX.Element => {
  if (venue.isVirtual) {
    return (
      <Callout title="Ce lieu vous permet uniquement de créer des offres numériques, il n’est pas visible sur l’application pass Culture.">
        Vous n’avez pas d’informations à remplir à destination du grand public.
        Si vous souhaitez modifier d’autres informations, vous pouvez vous
        rendre dans la page "Paramètres de l’activité".
      </Callout>
    )
  }

  return (
    <>
      {venue.isPermanent && (
        <>
          <div className={styles['page-status']}>
            <Callout title="Les informations que vous renseignez ci-dessous sont affichées dans votre page partenaire, visible sur l’application pass Culture" />
            <PartnerPageIndividualSection
              venueId={venue.id}
              isVisibleInApp={Boolean(venue.isVisibleInApp)}
            />
          </div>

          <hr className={styles['separator']} />
        </>
      )}

      <Routes>
        <Route path="" element={<VenueEditionReadOnly venue={venue} />} />
        <Route
          path="/edition"
          element={
            <VenueEditionForm venue={venue} reloadVenueData={reloadVenueData} />
          }
        />
      </Routes>
    </>
  )
}

import { useLocation } from 'react-router'

import { GetVenueResponseModel } from '@/apiClient/v1'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

interface VenueEditionProps {
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  venue,
}: VenueEditionProps): JSX.Element => {
  const shouldDisplayAccessToPageWarning =
    venue.isPermanent && venue.hasOffers && !venue.hasActiveIndividualOffer

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
      {shouldDisplayAccessToPageWarning && (
        <>
          <div className={styles['page-status']}>
            <Callout variant={CalloutVariant.WARNING}>
              Sans offre publiée, les jeunes n’ont pas accès à votre page sur
              l’application.
            </Callout>
          </div>
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

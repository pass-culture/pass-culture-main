import { useEffect, useState } from 'react'
import { useLocation, useSearchParams } from 'react-router-dom'

import { GetOffererResponseModel, VenueTypeResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { RedirectDialog } from 'components/Dialog/RedirectDialog/RedirectDialog'
import { SoftDeletedOffererWarning } from 'components/SoftDeletedOffererWarning/SoftDeletedOffererWarning'
import { Events } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'
import { VenueList } from 'pages/Home/Venues/VenueList'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { Card } from '../Card'

import { OffererCreationLinks } from './OffererCreationLinks'
import { OffererDetails } from './OffererDetails'
import styles from './Offerers.module.scss'
import { PartnerPages } from './PartnerPages'
import { VenueCreationLinks } from './VenueCreationLinks'

export interface OfferersProps {
  selectedOfferer: GetOffererResponseModel | null
  isLoading: boolean
  isUserOffererValidated: boolean
  offererOptions: SelectOption[]
  venueTypes: VenueTypeResponseModel[]
}

export const Offerers = ({
  offererOptions,
  selectedOfferer,
  isLoading,
  isUserOffererValidated,
  venueTypes,
}: OfferersProps) => {
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false)

  const location = useLocation()
  const [searchParams, setSearchParams] = useSearchParams()
  const { logEvent } = useAnalytics()

  useEffect(() => {
    location.search === '?success' && setOpenSuccessDialog(true)
  }, [location.search])

  if (isLoading) {
    return (
      <Card>
        <div className={styles['loader-container']}>
          <Spinner />
        </div>
      </Card>
    )
  }

  const removeSuccessParams = () => {
    if (searchParams.has('success')) {
      searchParams.delete('success')
      setSearchParams(searchParams, { replace: true })
    }
  }

  const isOffererSoftDeleted = selectedOfferer && !selectedOfferer.isActive
  const userHasOfferers = offererOptions.length > 0
  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  return (
    <>
      {userHasOfferers && (
        <>
          {selectedOfferer && openSuccessDialog && (
            <RedirectDialog
              icon={strokePartyIcon}
              redirectText="Créer une offre"
              redirectLink={{
                to: `/offre/creation?structure=${selectedOfferer.id}`,
                isExternal: false,
              }}
              cancelText="Plus tard"
              withRedirectLinkIcon={false}
              title="Félicitations,"
              secondTitle="vous avez créé votre lieu !"
              onCancel={() => {
                removeSuccessParams()
                setTimeout(() => window.hj?.('event', 'click_on_later'), 200)
                logEvent(
                  Events.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL,
                  {
                    from: location.pathname,
                  }
                )
                setOpenSuccessDialog(false)
              }}
              cancelIcon={fullWaitIcon}
            >
              <p>Vous pouvez dès à présent créer une offre.</p>
            </RedirectDialog>
          )}

          <h2 className={styles['title']}>Structure</h2>

          <OffererDetails
            isUserOffererValidated={isUserOffererValidated}
            offererOptions={offererOptions}
          />

          {selectedOfferer && permanentVenues.length > 0 && (
            <PartnerPages
              venues={permanentVenues}
              offerer={selectedOfferer}
              venueTypes={venueTypes}
            />
          )}

          {selectedOfferer && !isOffererSoftDeleted && (
            <>
              {/*
               * The whole sectionning of the homepage should be refactored to account
               * for the new blocks introduced by the partner page feature but it
               * is too complex to do so for now (it would require adding another level
               * of section nesting DOM depending on if the FF is on or not)
               * For now we use h3 here with manual margin, but will revise sectioning
               * with h2 and the homepage margin style once the WIP_PARTNER_PAGE FF is removed.
               */}
              <h3 className={styles['title']} style={{ marginTop: '16px' }}>
                Carnet d’adresses
              </h3>

              <p>
                Renseignez ci-dessous les lieux dans lesquels vous proposez vos
                offres. Si le lieu appartient à votre structure une page
                partenaire y sera automatiquement associée.
              </p>

              <VenueList offerer={selectedOfferer} />
            </>
          )}
        </>
      )}
      {
        /* istanbul ignore next: DEBT, TO FIX */ isUserOffererValidated &&
          isOffererSoftDeleted && <SoftDeletedOffererWarning />
      }

      {!userHasOfferers && <OffererCreationLinks />}

      <VenueCreationLinks offerer={selectedOfferer} />
    </>
  )
}

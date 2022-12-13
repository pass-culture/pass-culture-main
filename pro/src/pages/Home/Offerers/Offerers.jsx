import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import SoftDeletedOffererWarning from 'components/SoftDeletedOffererWarning'
import { Events } from 'core/FirebaseEvents/constants'
import { useNewOfferCreationJourney } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as StatusPendingFullIcon } from 'icons/ico-status-pending-full.svg'
import { ReactComponent as SuccessIcon } from 'icons/ico-success.svg'
import {
  INITIAL_PHYSICAL_VENUES,
  INITIAL_VIRTUAL_VENUE,
} from 'pages/Home/Offerers/_constants'
import { VenueList } from 'pages/Home/Venues'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByDisplayName } from 'utils/strings'

import OffererCreationLinks from './OffererCreationLinks'
import OffererDetails from './OffererDetails'
import VenueCreationLinks from './VenueCreationLinks'

export const CREATE_OFFERER_SELECT_ID = 'creation'

const Offerers = () => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [businessUnitList, setBusinessUnitList] = useState([])
  const [physicalVenues, setPhysicalVenues] = useState(INITIAL_PHYSICAL_VENUES)
  const [virtualVenue, setVirtualVenue] = useState(INITIAL_VIRTUAL_VENUE)
  const [isLoading, setIsLoading] = useState(true)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false)
  const location = useLocation()
  const history = useHistory()

  const hasNewOfferCreationJourney = useNewOfferCreationJourney()

  const { structure: offererId } = Object.fromEntries(
    new URLSearchParams(location.search)
  )

  const setQuery = offererId => {
    const frenchQueryString = `structure=${offererId}`
    history.push(`${location.pathname}?${frenchQueryString}`)
  }

  useEffect(
    function fetchData() {
      // RomainC: Challenge this function it is called each times
      // offererId change, this doesn't seem necessary
      api.listOfferersNames().then(receivedOffererNames => {
        const initialOffererOptions = sortByDisplayName(
          receivedOffererNames.offerersNames.map(item => ({
            id: item['id'].toString(),
            displayName: item['name'],
          }))
        )

        if (initialOffererOptions.length > 0) {
          setSelectedOffererId(offererId || initialOffererOptions[0].id)
          setOffererOptions([
            ...initialOffererOptions,
            {
              displayName: '+ Ajouter une structure',
              id: CREATE_OFFERER_SELECT_ID,
            },
          ])
        } else {
          setIsLoading(false)
        }
      })
    },
    [offererId]
  )

  useEffect(() => {
    if (hasNewOfferCreationJourney) {
      location.search === '?success' && setOpenSuccessDialog(true)
    }
  }, [hasNewOfferCreationJourney])

  useEffect(() => {
    async function loadOfferer(offererId) {
      try {
        const receivedOfferer = await api.getOfferer(offererId)
        setSelectedOfferer(receivedOfferer)
        setPhysicalVenues(
          receivedOfferer.managedVenues.filter(venue => !venue.isVirtual)
        )
        const virtualVenue = receivedOfferer.managedVenues.find(
          venue => venue.isVirtual
        )
        setVirtualVenue(virtualVenue)
        setIsUserOffererValidated(true)

        const receivedBusinessUnitList = await api.getBusinessUnits(offererId)
        setBusinessUnitList(receivedBusinessUnitList)
      } catch (error) {
        /* istanbul ignore next: DEBT, TO FIX */
        if (error.status === HTTP_STATUS.FORBIDDEN) {
          setSelectedOfferer({ id: offererId, managedVenues: [] })
          setBusinessUnitList([])
          setPhysicalVenues(INITIAL_PHYSICAL_VENUES)
          setVirtualVenue(INITIAL_VIRTUAL_VENUE)
          setIsUserOffererValidated(false)
        }
      }
      setIsLoading(false)
    }
    selectedOffererId && loadOfferer(selectedOffererId)
  }, [selectedOffererId])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId === CREATE_OFFERER_SELECT_ID) {
        history.push('/structures/creation')
      } else if (newOffererId !== selectedOfferer.id) {
        setSelectedOffererId(newOffererId)
        setQuery(newOffererId)
      }
    },
    [history, selectedOfferer, setQuery]
  )

  if (isLoading) {
    return (
      <div className="h-card h-card-secondary h-card-placeholder">
        <div className="h-card-inner">
          <Spinner />
        </div>
      </div>
    )
  }

  const removeSuccessParams = () => {
    if (hasNewOfferCreationJourney) {
      const queryParams = new URLSearchParams(location.search)
      if (queryParams.has('success')) {
        queryParams.delete('success')
        history.replace({
          search: queryParams.toString(),
        })
      }
    }
  }
  const { logEvent } = useAnalytics()
  const isOffererSoftDeleted =
    selectedOfferer && selectedOfferer.isActive === false
  const userHasOfferers = offererOptions.length > 0
  return (
    <>
      {userHasOfferers && selectedOfferer && (
        <>
          {openSuccessDialog && (
            <RedirectDialog
              icon={SuccessIcon}
              redirectText="Créer une offre"
              redirectLink={{
                to: `/offre/creation?structure=${selectedOfferer.id}`,
                isExternal: false,
              }}
              cancelText="Plus tard"
              withRedirectLinkIcon={false}
              title="Félicitations,"
              secondTitle="vous avez créé votre lieu !"
              onRedirect={() =>
                logEvent?.(
                  Events.CLICKED_CREATE_OFFER_FROM_SUCCESS_VENUE_CREATION_MODAL,
                  {
                    from: location.pathname,
                  }
                )
              }
              onCancel={() => {
                removeSuccessParams()
                logEvent?.(
                  Events.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL,
                  {
                    from: location.pathname,
                  }
                )
                setOpenSuccessDialog(false)
              }}
              cancelIcon={StatusPendingFullIcon}
            >
              <p>Vous pouvez dès à présent créer une offre.</p>
            </RedirectDialog>
          )}
          <h2 className="h-section-title">Structures et lieux</h2>
          <OffererDetails
            businessUnitList={businessUnitList}
            handleChangeOfferer={handleChangeOfferer}
            hasPhysicalVenues={physicalVenues.length > 0}
            isUserOffererValidated={isUserOffererValidated}
            offererOptions={offererOptions}
            selectedOfferer={selectedOfferer}
          />

          {!isOffererSoftDeleted && (
            <VenueList
              physicalVenues={physicalVenues}
              selectedOffererId={selectedOfferer.id}
              virtualVenue={
                selectedOfferer.hasDigitalVenueAtLeastOneOffer
                  ? virtualVenue
                  : null
              }
            />
          )}
        </>
      )}

      {
        /* istanbul ignore next: DEBT, TO FIX */ isOffererSoftDeleted && (
          <SoftDeletedOffererWarning />
        )
      }

      {!userHasOfferers && <OffererCreationLinks />}

      {isUserOffererValidated &&
        !isOffererSoftDeleted &&
        physicalVenues.length > 0 && (
          <VenueCreationLinks
            hasPhysicalVenue={physicalVenues.length > 0}
            hasVirtualOffers={
              !!virtualVenue && !!selectedOfferer.hasDigitalVenueAtLeastOneOffer
            }
            offererId={
              /* istanbul ignore next: DEBT, TO FIX */ selectedOfferer
                ? selectedOfferer.id
                : null
            }
          />
        )}
    </>
  )
}

export default Offerers

import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'

import {
  GetOffererResponseModel,
  GetOfferersNamesResponseModel,
} from 'apiClient/v1'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import SoftDeletedOffererWarning from 'components/SoftDeletedOffererWarning'
import { Events } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'
import { VenueList } from 'pages/Home/Venues/VenueList'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import { Card } from '../Card'

import OffererCreationLinks from './OffererCreationLinks'
import OffererDetails from './OffererDetails'
import styles from './Offerers.module.scss'
import { PartnerPages } from './PartnerPages'
import VenueCreationLinks from './VenueCreationLinks'

const CREATE_OFFERER_SELECT_ID = 'creation'

export interface OfferersProps {
  receivedOffererNames?: GetOfferersNamesResponseModel | null
  onSelectedOffererChange: (offererId: string) => void
  cancelLoading: () => void
  selectedOfferer?: GetOffererResponseModel | null
  isLoading: boolean
  isUserOffererValidated: boolean
}

const Offerers = ({
  receivedOffererNames,
  onSelectedOffererChange,
  cancelLoading,
  selectedOfferer,
  isLoading,
  isUserOffererValidated,
}: OfferersProps) => {
  const isPartnerPageActive = useActiveFeature('WIP_PARTNER_PAGE')
  const [offererOptions, setOffererOptions] = useState<SelectOption[]>([])
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false)

  const location = useLocation()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { logEvent } = useAnalytics()

  const offererId = searchParams.get('structure')

  useEffect(() => {
    if (receivedOffererNames) {
      if (receivedOffererNames.offerersNames.length > 0) {
        const initialOffererOptions = sortByLabel(
          receivedOffererNames.offerersNames.map((item) => ({
            value: item['id'].toString(),
            label: item['name'],
          }))
        )
        onSelectedOffererChange(offererId ?? initialOffererOptions[0].value)
        setOffererOptions([
          ...initialOffererOptions,
          {
            label: '+ Ajouter une structure',
            value: CREATE_OFFERER_SELECT_ID,
          },
        ])
      } else {
        cancelLoading()
      }
    }
  }, [offererId, receivedOffererNames])

  useEffect(() => {
    location.search === '?success' && setOpenSuccessDialog(true)
  }, [])

  const handleChangeOfferer = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newOffererId = event.target.value
    if (newOffererId === CREATE_OFFERER_SELECT_ID) {
      navigate('/structures/creation')
    } else if (newOffererId !== selectedOfferer?.id.toString()) {
      onSelectedOffererChange(newOffererId)
      searchParams.set('structure', newOffererId)
      setSearchParams(searchParams)
    }
  }

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

  const isOffererSoftDeleted =
    selectedOfferer && selectedOfferer.isActive === false
  const userHasOfferers = offererOptions.length > 0
  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  return (
    <>
      {userHasOfferers && selectedOfferer && (
        <>
          {openSuccessDialog && (
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
                logEvent?.(
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

          {isPartnerPageActive ? (
            <h2 className={styles['title']}>Structure</h2>
          ) : (
            <h2 className={styles['title']}>Structures et lieux</h2>
          )}

          <OffererDetails
            handleChangeOfferer={handleChangeOfferer}
            isUserOffererValidated={isUserOffererValidated}
            offererOptions={offererOptions}
            selectedOfferer={selectedOfferer}
          />

          {isPartnerPageActive && permanentVenues.length > 0 && (
            <PartnerPages venues={permanentVenues} offerer={selectedOfferer} />
          )}

          {!isOffererSoftDeleted && (
            <>
              {isPartnerPageActive && (
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
                    Renseignez ci-dessous les lieux dans lesquels vous proposez
                    vos offres. Si le lieu appartient à votre structure une page
                    partenaire y sera automatiquement associée.
                  </p>
                </>
              )}

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

export default Offerers

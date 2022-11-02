import React, { useCallback, useState } from 'react'

import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as ExternalSiteIcon } from 'icons/ico-external-site-filled.svg'
import { FormLayout } from 'new_components/FormLayout'
import { ReimbursementPointV2 } from 'new_components/VenueForm/ReimbursementPointV2'
import InternalBanner from 'ui-kit/Banners/InternalBanner'

import PricingPoint from '../PricingPoint/PricingPoint'
import PricingPointV2 from '../PricingPointV2'
import { ReimbursementPoint } from '../ReimbursementPoint'

export interface ReimbursementInterface {
  offerer: GetOffererResponseModel
  readOnly: boolean
  scrollToSection?: boolean
  venue: GetVenueResponseModel
}

const ReimbursementFields = ({
  offerer,
  readOnly,
  scrollToSection,
  venue,
}: ReimbursementInterface) => {
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
  const createVenuePath = `/structures/${offerer.id}/lieux/creation`
  const [venueHasPricingPoint, setVenueHasPricingPoint] = useState<boolean>(
    !!venue.pricingPoint
  )

  const scrollToReimbursementSection = useCallback((node: any) => {
    if (scrollToSection) {
      setTimeout(() => {
        node.scrollIntoView()
      }, 200)
    }
  }, [])
  const isVenueFormV2 = useActiveFeature('VENUE_FORM_V2')
  return (
    <>
      <div ref={scrollToReimbursementSection}>
        <FormLayout.Section title="Remboursement">
          {!venueHaveSiret && !offererHaveVenueWithSiret ? (
            <InternalBanner
              to={createVenuePath}
              Icon={ExternalSiteIcon}
              linkTitle="Créer un lieu avec SIRET"
            >
              Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
              devez avoir, au minimum, un lieu rattaché à un SIRET.
            </InternalBanner>
          ) : (
            <>
              {!venueHaveSiret &&
                (isVenueFormV2 ? (
                  <PricingPointV2
                    readOnly={readOnly}
                    offerer={offerer}
                    venue={venue}
                    setVenueHasPricingPoint={setVenueHasPricingPoint}
                  />
                ) : (
                  <PricingPoint
                    readOnly={readOnly}
                    offerer={offerer}
                    venue={venue}
                    setVenueHasPricingPoint={setVenueHasPricingPoint}
                  />
                ))}

              {isVenueFormV2 ? (
                <ReimbursementPointV2
                  offerer={offerer}
                  readOnly={readOnly}
                  initialVenue={venue}
                  venueHasPricingPoint={venueHasPricingPoint}
                />
              ) : (
                <ReimbursementPoint
                  offerer={offerer}
                  readOnly={readOnly}
                  initialVenue={venue}
                  venueHasPricingPoint={venueHasPricingPoint}
                />
              )}
            </>
          )}
        </FormLayout.Section>
      </div>
    </>
  )
}

export default ReimbursementFields

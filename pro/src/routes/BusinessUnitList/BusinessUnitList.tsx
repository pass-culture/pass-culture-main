import React, { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router'

import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import BusinessUnitListScreen from 'screens/BusinessUnitList'
import {
  IBusinessUnit,
  IBusinessUnitVenue,
  IOfferer,
} from 'screens/BusinessUnitList/BusinessUnitList'

interface IAPIBusinessUnitListItem {
  bic: string
  id: number
  iban: string
  name: string
  siret: string | null
}

const BusinessUnitList = (): JSX.Element => {
  const [offerer, setOfferer] = useState<IOfferer | null>(null)
  const [businessUnitList, setBusinessUnitList] = useState<
    IBusinessUnit[] | null
  >(null)
  const [venues, setVenues] = useState<IBusinessUnitVenue[] | null>(null)

  const params = useParams<{ offererId: string }>()

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      const offererResponse = await pcapi.getOfferer(offererId)
      setOfferer({
        id: offererResponse.id,
        name: offererResponse.name,
        hasDigitalVenueAtLeastOneOffer:
          offererResponse.hasDigitalVenueAtLeastOneOffer,
      })
    }

    async function loadBusinessUnitList(offererId: string) {
      const businessUnitListResponse: IAPIBusinessUnitListItem[] =
        await pcapi.getBusinessUnits(offererId)
      const serializedBusinessUnitList: IBusinessUnit[] =
        businessUnitListResponse.map(
          (apiBusinessUnit: IAPIBusinessUnitListItem): IBusinessUnit => {
            return {
              id: apiBusinessUnit.id,
              name: apiBusinessUnit.name,
              bic: apiBusinessUnit.bic,
              iban: apiBusinessUnit.iban,
              siret: apiBusinessUnit.siret,
            }
          }
        )
      setBusinessUnitList(serializedBusinessUnitList)
    }

    async function loadVenues(offererId: string) {
      const venuesForOffererResponse = await pcapi.getVenuesForOfferer({
        offererId,
      })
      const serializedVenueList: IBusinessUnitVenue[] =
        venuesForOffererResponse.map((apiVenue): IBusinessUnitVenue => {
          return {
            id: apiVenue.id,
            name: apiVenue.name,
            publicName: apiVenue.publicName,
            siret: apiVenue.siret,
            businessUnitId: apiVenue.businessUnitId,
            managingOffererId: apiVenue.managingOffererId,
            isBusinessUnitMainVenue: apiVenue.isBusinessUnitMainVenue,
            isVirtual: apiVenue.isVirtual,
          }
        })

      setVenues(serializedVenueList)
    }

    loadOfferer(params.offererId)
    loadBusinessUnitList(params.offererId)
    loadVenues(params.offererId)
  }, [params.offererId])

  const saveBusinessUnit = useCallback((businessUnitId, siret) => {
    try {
      pcapi.editBusinessUnit(businessUnitId, siret)
    } catch (e) {
      console.error(e)
    }
  }, [])

  if (!businessUnitList || !offerer || !venues) {
    return <Spinner />
  }

  return (
    <BusinessUnitListScreen
      businessUnitList={businessUnitList}
      offerer={offerer}
      saveBusinessUnit={saveBusinessUnit}
      venues={venues}
    />
  )
}

export default BusinessUnitList

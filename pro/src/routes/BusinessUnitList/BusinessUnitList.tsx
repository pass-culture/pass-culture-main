import React, { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import Spinner from 'components/layout/Spinner'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import BusinessUnitListScreen from 'screens/BusinessUnitList'
import {
  IBusinessUnit,
  IBusinessUnitVenue,
  IOfferer,
} from 'screens/BusinessUnitList/BusinessUnitList'

const BusinessUnitList = (): JSX.Element => {
  const [offerer, setOfferer] = useState<IOfferer | null>(null)
  const [businessUnitList, setBusinessUnitList] = useState<
    IBusinessUnit[] | null
  >(null)
  const [venues, setVenues] = useState<IBusinessUnitVenue[] | null>(null)

  const params = useParams<{ offererId: string }>()

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      const offererResponse = await api.getOfferer(offererId)
      setOfferer({
        id: offererResponse.id,
        name: offererResponse.name,
        hasDigitalVenueAtLeastOneOffer:
          offererResponse.hasDigitalVenueAtLeastOneOffer,
      })
    }

    async function loadBusinessUnitList(offererId: string) {
      const businessUnitListResponse =
        // @ts-expect-error string is not assignable to type number
        await api.getBusinessUnits(offererId)
      const serializedBusinessUnitList: IBusinessUnit[] =
        businessUnitListResponse.map((apiBusinessUnit): IBusinessUnit => {
          return {
            id: apiBusinessUnit.id,
            name: apiBusinessUnit.name,
            bic: apiBusinessUnit.bic ?? '',
            iban: apiBusinessUnit.iban ?? '',
            siret: apiBusinessUnit.siret ?? '',
          }
        })
      setBusinessUnitList(serializedBusinessUnitList)
    }

    async function loadVenues(offererId: string) {
      const venuesForOffererResponse = await getVenuesForOffererAdapter({
        offererId,
      })
      const serializedVenueList: IBusinessUnitVenue[] =
        venuesForOffererResponse.payload.map((apiVenue): IBusinessUnitVenue => {
          return {
            id: apiVenue.id,
            name: apiVenue.name,
            publicName: apiVenue.publicName,
            siret: apiVenue.siret,
            businessUnitId: apiVenue.businessUnitId,
            managingOffererId: apiVenue.managingOffererId,
            isBusinessUnitMainVenue: apiVenue.isBusinessUnitMainVenue,
            isVirtual: apiVenue.isVirtual,
          } as IBusinessUnitVenue // FIXME: (MathildeDuboille - 2022-09-29) types does not match with IBusinessUnitVenue
        })

      setVenues(serializedVenueList)
    }

    loadOfferer(params.offererId)
    loadBusinessUnitList(params.offererId)
    loadVenues(params.offererId)
  }, [params.offererId])

  const saveBusinessUnit = useCallback(
    (businessUnitId: number, siret: string) => {
      try {
        api.editBusinessUnit(businessUnitId, { siret })
      } catch (e) {
        // FIX ME
        // eslint-disable-next-line
        console.error(e)
      }
    },
    []
  )

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

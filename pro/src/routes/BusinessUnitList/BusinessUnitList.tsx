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

import styles from './BusinessUnitCard.module.scss'

const BusinessUnitList = (): JSX.Element => {
  const [offerer, setOfferer] = useState<IOfferer | null>(null)
  const [businessUnitList, setBusinessUnitList] = useState<
    IBusinessUnit[] | null
  >(null)
  const [venues, setVenues] = useState<IBusinessUnitVenue[] | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)

  const params = useParams<{ offererId: string }>()

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      const offererResponse: any = await pcapi.getOfferer(offererId)
      setOfferer({
        id: offererResponse.id,
        name: offererResponse.name,
      })
    }

    async function loadBusinessUnitList(offererId: string) {
      const businessUnitListResponse: any = await pcapi.getBusinessUnitList(
        offererId
      )
      const serializedBusinessUnitList: IBusinessUnit[] =
        businessUnitListResponse.map((apiBusinessUnit: any): IBusinessUnit => {
          return {
            id: apiBusinessUnit.id,
            name: apiBusinessUnit.name,
            bic: apiBusinessUnit.bic,
            iban: apiBusinessUnit.iban,
            siret: apiBusinessUnit.siret,
          }
        })
      setBusinessUnitList(serializedBusinessUnitList)
    }

    async function loadVenues(offererId: string) {
      const venuesForOffererResponse: any = await pcapi.getVenuesForOfferer({
        offererId
      })
      let serializedVenueList: IBusinessUnitVenue[] =
      venuesForOffererResponse.map((apiVenue: any): IBusinessUnitVenue => {
        return {
          id: apiVenue.id,
          name: apiVenue.name,
          siret: apiVenue.siret,
          businessUnitId: apiVenue.businessUnitId,
          managingOffererId: apiVenue.managingOffererId,
        }
      })
      serializedVenueList = [
        ...serializedVenueList,
        ...venuesForOffererResponse.map((apiVenue: any): IBusinessUnitVenue => {
          return {
            id: apiVenue.id,
            name: apiVenue.name,
            siret: apiVenue.siret,
            businessUnitId: apiVenue.businessUnitId,
            managingOffererId: apiVenue.managingOffererId,
          }
        })
      ]
      serializedVenueList = [
        ...serializedVenueList,
        ...venuesForOffererResponse.map((apiVenue: any): IBusinessUnitVenue => {
          return {
            id: apiVenue.id,
            name: apiVenue.name,
            siret: 'TEST SIRET',
            businessUnitId: apiVenue.businessUnitId,
            managingOffererId: apiVenue.managingOffererId,
          }
        })
      ]
      serializedVenueList = [
        ...serializedVenueList,
        ...venuesForOffererResponse.map((apiVenue: any): IBusinessUnitVenue => {
          return {
            id: apiVenue.id,
            name: apiVenue.name,
            siret: apiVenue.siret,
            businessUnitId: apiVenue.businessUnitId,
            managingOffererId: apiVenue.managingOffererId,
          }
        })
      ]

      setVenues(serializedVenueList)
    }

    loadOfferer(params.offererId)
    loadBusinessUnitList(params.offererId)
    loadVenues(params.offererId)
  }, [params.offererId])

  useEffect(() => {
    setIsReady(
      businessUnitList !== null
      && offerer !== null
      && venues !== null
    )
  }, [businessUnitList, offerer, venues])

  const saveBusinessUnit = useCallback(() => {}, [])

  if (!isReady) {
    return <Spinner />
  }

  return (
    <BusinessUnitListScreen
      businessUnitList={businessUnitList!}
      offerer={offerer!}
      saveBusinessUnit={saveBusinessUnit}
      venues={venues!}
    />
  )
}

export default BusinessUnitList

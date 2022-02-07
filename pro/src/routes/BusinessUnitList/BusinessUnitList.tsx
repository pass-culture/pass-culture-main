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

interface IAPIVenue {
  address: string | null
  bookingEmail: string | null
  businessUnitId: number | null
  city: string | null
  comment: string | null
  departementCode: string | null
  id: string
  isValidated: boolean
  isVirtual: boolean
  managingOffererId: string
  name: string
  postalCode: string | null
  publicName: string
  venueLabelId: string | null
  venueTypeCode: string | null
  withdrawalDetails: string | null
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  siret: string | null
  isBusinessUnitMainVenue: boolean | null
}

interface IAPIOfferer {
  address: string | null
  apiKey: {
    maxAllowed: number
    prefixes: string[]
  }
  bic: string | null
  city: string | null
  dateCreated: string | null
  dateModifiedAtLastProvider: string | null
  demarchesSimplifieesApplicationId: string | null
  fieldsUpdated: []
  hasDigitalVenueAtLeastOneOffer: boolean
  hasMissingBankInformation: boolean
  iban: string | null
  id: string
  isValidated: boolean
  lastProviderId: string | null
  managedVenues: IAPIVenue[]
  name: string
  postalCode: string | null
  siren: string
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
      const offererResponse: IAPIOfferer = await pcapi.getOfferer(offererId)
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
      const venuesForOffererResponse: IAPIVenue[] =
        await pcapi.getVenuesForOfferer({
          offererId,
        })
      const serializedVenueList: IBusinessUnitVenue[] =
        venuesForOffererResponse.map(
          (apiVenue: IAPIVenue): IBusinessUnitVenue => {
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
          }
        )

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

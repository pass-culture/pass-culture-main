import { useEffect, useState } from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import { PartnerPage } from './PartnerPage'
import styles from './PartnerPages.module.scss'

export const SAVED_VENUE_ID_KEY = 'homepageSelectedVenueId'

const getSavedVenueId = (
  venues: Map<string, GetOffererVenueResponseModel>
): string | null => {
  const isLocalStorageAvailable = localStorageAvailable()
  if (!isLocalStorageAvailable) {
    return null
  }

  const savedVenueId = localStorage.getItem(SAVED_VENUE_ID_KEY)
  return venues.has(savedVenueId ?? '') ? savedVenueId : null
}

export interface PartnerPagesProps {
  offerer: GetOffererResponseModel
  venues: GetOffererVenueResponseModel[]
  setSelectedOfferer: (offerer: GetOffererResponseModel) => void
}

export const PartnerPages = ({
  venues,
  offerer,
  setSelectedOfferer,
}: PartnerPagesProps) => {
  const [venuesOptions, setVenuesOptions] = useState<SelectOption[]>([])
  const [mapVenues, setMapVenues] = useState<
    Map<string, GetOffererVenueResponseModel>
  >(new Map())
  const [selectedVenueId, setSelectedVenueId] = useState<string>('')

  useEffect(() => {
    const options = []
    const map = new Map()
    for (const venue of venues) {
      options.push({
        label: venue.publicName || venue.name,
        value: venue.id.toString(),
      })
      map.set(venue.id.toString(), venue)
    }
    setVenuesOptions(options)
    setMapVenues(map)
    setSelectedVenueId(
      venues.length > 0 ? getSavedVenueId(map) ?? venues[0].id.toString() : ''
    )
  }, [venues])

  const selectedVenue = mapVenues.get(selectedVenueId) ?? venues[0]

  return (
    <section className={styles['section']}>
      <h3 className={styles['title']}>
        {venues.length === 1 ? 'Votre page partenaire' : 'Vos pages partenaire'}
      </h3>

      <p className={styles['description']}>
        Complétez vos informations pour présenter votre activité au grand public
        sur le site et l’application pass Culture à destination des jeunes et /
        ou auprès des enseignants sur la plateforme Adage.
      </p>

      {venues.length > 1 && (
        <>
          <FieldLayout label="Sélectionnez votre page partenaire" name="venues">
            <SelectInput
              name="venues"
              options={venuesOptions}
              value={selectedVenueId}
              onChange={(e) => {
                setSelectedVenueId(e.target.value)
                if (localStorageAvailable()) {
                  localStorage.setItem(SAVED_VENUE_ID_KEY, e.target.value)
                }
              }}
            />
          </FieldLayout>
        </>
      )}

      {selectedVenue && (
        <PartnerPage
          offerer={offerer}
          venue={selectedVenue}
          setSelectedOfferer={setSelectedOfferer}
          // In order to have the image state changing in PartnerPage,
          // we wanna the state reset when the venue change, see :
          // https://react.dev/learn/preserving-and-resetting-state#option-2-resetting-state-with-a-key
          key={selectedVenue.id}
        />
      )}
    </section>
  )
}

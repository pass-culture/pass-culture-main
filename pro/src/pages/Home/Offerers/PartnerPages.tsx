import React, { useState } from 'react'

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
  venues: GetOffererVenueResponseModel[]
): string | null => {
  const isLocalStorageAvailable = localStorageAvailable()
  if (!isLocalStorageAvailable) {
    return null
  }

  const savedVenueId = localStorage.getItem(SAVED_VENUE_ID_KEY)
  if (
    !savedVenueId ||
    !venues.map((venue) => String(venue.id)).includes(savedVenueId)
  ) {
    return null
  }

  return savedVenueId
}

export interface PartnerPagesProps {
  offerer: GetOffererResponseModel
  venues: GetOffererVenueResponseModel[]
}

export const PartnerPages = ({ venues, offerer }: PartnerPagesProps) => {
  const venuesOptions: SelectOption[] = venues.map((venue) => ({
    label: venue.name,
    value: venue.id.toString(),
  }))
  const [selectedVenueId, setSelectedVenueId] = useState<string>(
    venues.length > 0 ? getSavedVenueId(venues) ?? venues[0].id.toString() : ''
  )
  const selectedVenue =
    venues.find((venue) => venue.id.toString() === selectedVenueId) ?? venues[0]

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

      {selectedVenue && <PartnerPage offerer={offerer} venue={selectedVenue} />}
    </section>
  )
}

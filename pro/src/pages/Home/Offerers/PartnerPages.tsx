import React, { useState } from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'

import styles from './PartnerPages.module.scss'

export interface PartnerPagesProps {
  venues: GetOffererVenueResponseModel[]
}

export const PartnerPages = ({ venues }: PartnerPagesProps) => {
  const venuesOptions: SelectOption[] = venues.map((venue) => ({
    label: venue.name,
    value: venue.id.toString(),
  }))
  const [selectedVenue, setSelectedVenue] = useState<string>(
    venues.length > 0 ? venues[0].id.toString() : ''
  )

  return (
    <section className={styles['section']}>
      {venues.length === 1 ? (
        <>
          <h3 className={styles['title']}>Votre page partenaire</h3>
          <p>
            Les pages partenaires vous permettent de présenter votre activité.
          </p>
        </>
      ) : (
        <>
          <h3 className={styles['title']}>Vos pages partenaire</h3>

          <FieldLayout label="Sélectionnez votre page partenaire" name="venues">
            <SelectInput
              name="venues"
              options={venuesOptions}
              value={selectedVenue}
              onChange={(e) => setSelectedVenue(e.target.value)}
            />
          </FieldLayout>
        </>
      )}
    </section>
  )
}

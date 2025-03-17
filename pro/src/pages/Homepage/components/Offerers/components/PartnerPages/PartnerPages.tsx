import { useState } from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { SelectOption } from 'commons/custom_types/form'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import { PartnerPage } from './components/PartnerPage'
import styles from './PartnerPages.module.scss'

export interface PartnerPagesProps {
  offerer: GetOffererResponseModel
  venues: GetOffererVenueResponseModel[]
  venueTypes: VenueTypeResponseModel[]
}

export const PartnerPages = ({
  venues,
  offerer,
  venueTypes,
}: PartnerPagesProps) => {
  const [selectedVenueId, setSelectedVenueId] = useState<string>(
    venues.length > 0
      ? venues[0].id.toString()
      : ''
  )

  const venuesOptions: SelectOption[] = venues.map((venue) => ({
    label: venue.publicName || venue.name,
    value: venue.id.toString(),
  }))
  const selectedVenue =
    venues.find((venue) => venue.id.toString() === selectedVenueId) ??
    (venues.length > 0 ? venues[0] : undefined)

  return (
    <section className={styles['section']}>
      <h3 className={styles['title']}>
        {venues.length === 1 ? 'Votre page partenaire' : 'Vos pages partenaire'}
      </h3>

      <p className={styles['description']}>
        Complétez vos informations pour présenter votre activité au grand public
        sur le site et l’application pass Culture à destination des jeunes et /
        ou auprès des enseignants sur la plateforme ADAGE.
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
              }}
            />
          </FieldLayout>
        </>
      )}

      {selectedVenue && (
        <PartnerPage
          offerer={offerer}
          venue={selectedVenue}
          venueTypes={venueTypes}
          // In order to have the image state changing in PartnerPage,
          // we wanna the state reset when the venue change, see :
          // https://react.dev/learn/preserving-and-resetting-state#option-2-resetting-state-with-a-key
          key={selectedVenue.id}
        />
      )}
    </section>
  )
}

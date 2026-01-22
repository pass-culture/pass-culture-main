import { useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import type { SelectOption } from '@/commons/custom_types/form'
import { pluralizeFr } from '@/commons/utils/pluralize'
import {
  getSavedPartnerPageVenueId,
  setSavedPartnerPageVenueId,
} from '@/commons/utils/savedPartnerPageVenueId'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Select } from '@/ui-kit/form/Select/Select'

import { PartnerPage } from './components/PartnerPage'
import styles from './PartnerPages.module.scss'

export interface PartnerPagesProps {
  offerer: GetOffererResponseModel
  venues: GetOffererVenueResponseModel[]
}

export const PartnerPages = ({ venues, offerer }: PartnerPagesProps) => {
  const savedPartnerPageVenueId = getSavedPartnerPageVenueId(
    'homepage',
    offerer.id
  )
  const stillRelevantSavedPartnerPageVenueId = venues
    .find((venue) => venue.id.toString() === savedPartnerPageVenueId)
    ?.id.toString()
  const initialSavedPartnerPageVenueId =
    stillRelevantSavedPartnerPageVenueId || venues[0].id.toString() || ''

  const [selectedVenueId, setSelectedVenueId] = useState<string>(
    initialSavedPartnerPageVenueId
  )

  const venuesOptions: SelectOption[] = venues.map((venue) => ({
    label: venue.publicName,
    value: venue.id.toString(),
  }))
  const selectedOffererVenue =
    venues.find((venue) => venue.id.toString() === selectedVenueId) ??
    (venues.length > 0 ? venues[0] : undefined)

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, selectedVenueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  return (
    <section className={styles['section']}>
      <h2 className={styles['title']}>
        {pluralizeFr(
          venues.length,
          'Votre page partenaire',
          'Vos pages partenaire'
        )}
      </h2>

      <p className={styles['description']}>
        Complétez vos informations pour présenter votre activité au grand public
        sur le site et l’application pass Culture à destination des jeunes et /
        ou auprès des enseignants sur la plateforme ADAGE.
      </p>

      {venues.length > 1 && (
        <FormLayout>
          <FormLayout.Row mdSpaceAfter>
            <Select
              label="Sélectionnez votre page partenaire"
              name="venues"
              options={venuesOptions}
              value={selectedVenueId}
              onChange={(e) => {
                setSelectedVenueId(e.target.value)
                setSavedPartnerPageVenueId(
                  'homepage',
                  offerer.id,
                  e.target.value
                )
              }}
              required={true}
            />
          </FormLayout.Row>
        </FormLayout>
      )}

      {venue && (
        <PartnerPage
          offerer={offerer}
          venue={venue}
          // In order to have the image state changing in PartnerPage,
          // we wanna the state reset when the venue change, see :
          // https://react.dev/learn/preserving-and-resetting-state#option-2-resetting-state-with-a-key
          key={venue.id}
          venueHasPartnerPage={selectedOffererVenue?.hasPartnerPage ?? false}
        />
      )}
    </section>
  )
}

import { useFieldArray, useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { ArtistType } from '@/apiClient/v1'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { ApiSelect } from '@/ui-kit/form/ApiSelect/ApiSelect'

const ARTIST_TYPE_LABELS: Record<ArtistType, string> = {
  [ArtistType.AUTHOR]: 'Auteur',
  [ArtistType.PERFORMER]: 'Interprète',
  [ArtistType.STAGE_DIRECTOR]: 'Metteur en scène',
}

type ArtistFieldProps = {
  readOnly: boolean
  artistType: ArtistType
}

export function ArtistField({
  readOnly,
  artistType,
}: Readonly<ArtistFieldProps>) {
  const { control, register } = useFormContext<DetailsFormValues>()

  const { fields } = useFieldArray({
    control,
    name: 'artistOfferLinks',
  })

  const fieldsForType = fields
    .map((field, index) => ({ field, index }))
    .filter(({ field }) => field.artistType === artistType)

  return (
    <>
      {fieldsForType.map(({ field, index }) => {
        const { onChange } = register(`artistOfferLinks.${index}`)
        const { ref } = register(`artistOfferLinks.${index}.artistName`)
        const name = `artistOfferLinks.${index}`

        return (
          <div key={field.id}>
            <ApiSelect
              name={name}
              label={ARTIST_TYPE_LABELS[artistType]}
              onSelect={(artist) => {
                if (artist) {
                  onChange({
                    target: {
                      name,
                      value: {
                        artistId: artist.id,
                        artistName: artist.name,
                        artistType,
                      },
                    },
                    type: 'change',
                  })
                }
              }}
              onSearch={(searchText) => {
                onChange({
                  target: {
                    name,
                    value: {
                      artistId: null,
                      artistName: searchText,
                      artistType,
                    },
                  },
                  type: 'change',
                })
              }}
              searchApi={async (searchText) => {
                const artists = await api.getArtists(searchText)

                return artists.map((artist) => ({
                  ...artist,
                  value: artist.id,
                  label: artist.name,
                }))
              }}
              minSearchLength={2}
              disabled={readOnly}
              required={false}
              ref={ref}
            />
          </div>
        )
      })}
    </>
  )
}

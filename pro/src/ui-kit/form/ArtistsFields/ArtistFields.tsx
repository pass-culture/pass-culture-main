import { useFieldArray, useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { ArtistType } from '@/apiClient/v1'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'

import { ApiSelect } from '../ApiSelect/ApiSelect'

const ARTIST_TYPE_LABELS: Record<ArtistType, string> = {
  [ArtistType.AUTHOR]: 'Auteur',
  [ArtistType.PERFORMER]: 'Interprète',
  [ArtistType.STAGE_DIRECTOR]: 'Metteur en scène',
}

type ArtistFieldsProps = {
  readOnly: boolean
  artistType: ArtistType
}

export function ArtistFields({ readOnly, artistType }: ArtistFieldsProps) {
  const { control, register } = useFormContext<DetailsFormValues>()

  const { fields } = useFieldArray({
    control,
    name: 'artists',
  })

  const fieldsOfType = fields
    .map((field, index) => ({ field, index }))
    .filter(({ field }) => field.artistType === artistType)

  return (
    <>
      {fieldsOfType.map(({ field, index }) => {
        const { onChange } = register(`artists.${index}`)
        const { ref } = register(`artists.${index}.artistName`)
        const name = `artists.${index}`

        return (
          <div key={field.id}>
            <ApiSelect
              name={name}
              label={ARTIST_TYPE_LABELS[artistType]}
              onOptionChosen={(artist) => {
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
              onOptionSearched={(searchText) => {
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
              getDataFromSearchText={async (searchText) => {
                const artists = await api.getArtists(searchText)

                return artists.map((artist) => ({
                  ...artist,
                  value: artist.id,
                  label: artist.name,
                }))
              }}
              minSearchLength={2}
              disabled={readOnly}
              ref={ref}
            />
          </div>
        )
      })}
    </>
  )
}

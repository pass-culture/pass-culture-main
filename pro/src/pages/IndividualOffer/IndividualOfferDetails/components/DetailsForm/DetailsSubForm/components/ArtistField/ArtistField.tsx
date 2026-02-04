import { useFieldArray, useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { type ArtistResponseModel, ArtistType } from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullMoreIcon from '@/icons/full-more.svg'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { ApiSelect } from '@/ui-kit/form/ApiSelect/ApiSelect'

const ARTIST_TYPE_LABELS: Record<ArtistType, string> = {
  [ArtistType.AUTHOR]: 'Auteur',
  [ArtistType.PERFORMER]: 'Interprète',
  [ArtistType.STAGE_DIRECTOR]: 'Metteur en scène',
}

type ArtistOption = ArtistResponseModel & { value: string; label: string }

type ArtistFieldProps = {
  readOnly: boolean
  artistType: ArtistType
}

export function ArtistField({
  readOnly,
  artistType,
}: Readonly<ArtistFieldProps>) {
  const {
    control,
    register,
    setValue,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const { fields, append } = useFieldArray({
    control,
    name: 'artistOfferLinks',
  })

  const fieldsForType = fields
    .map((field, index) => ({ field, index }))
    .filter(({ field }) => field.artistType === artistType)

  return (
    <>
      {fieldsForType.map(({ field, index }) => {
        const { ref } = register(`artistOfferLinks.${index}.artistName`)
        const name = `artistOfferLinks.${index}`

        return (
          <div key={field.id}>
            <ApiSelect
              name={name}
              label={ARTIST_TYPE_LABELS[artistType]}
              onSelect={(artist: ArtistOption) => {
                if (artist) {
                  setValue(
                    `artistOfferLinks.${index}`,
                    {
                      artistId: artist.id,
                      artistName: artist.name,
                      artistType,
                    },
                    { shouldValidate: true }
                  )
                }
              }}
              onSearch={(searchText) => {
                setValue(
                  `artistOfferLinks.${index}`,
                  {
                    artistId: null,
                    artistName: searchText,
                    artistType,
                  },
                  { shouldValidate: true }
                )
              }}
              searchApi={async (searchText) => {
                const artists = await api.getArtists(searchText)

                return artists.map((artist) => ({
                  ...artist,
                  value: artist.id,
                  label: artist.name,
                }))
              }}
              error={errors?.artistOfferLinks?.[index]?.artistName?.message}
              minSearchLength={2}
              disabled={readOnly}
              required={false}
              ref={ref}
            />
          </div>
        )
      })}
      {!readOnly && (
        <Button
          variant={ButtonVariant.TERTIARY}
          icon={fullMoreIcon}
          color={ButtonColor.NEUTRAL}
          label={`Ajouter un ${ARTIST_TYPE_LABELS[artistType].toLowerCase()}`}
          onClick={() =>
            append(
              { artistId: null, artistName: '', artistType },
              { shouldFocus: true }
            )
          }
        />
      )}
    </>
  )
}

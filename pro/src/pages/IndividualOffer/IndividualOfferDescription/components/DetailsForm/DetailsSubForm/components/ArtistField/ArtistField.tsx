import { type UseFieldArrayReturn, useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { type ArtistResponseModel, ArtistType } from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { resizeImageURL } from '@/commons/utils/resizeImageURL'
import { truncateAtWord } from '@/commons/utils/string'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { ApiSelect } from '@/ui-kit/form/ApiSelect/ApiSelect'

import styles from './ArtistField.module.scss'
import avatarPlaceholder from './assets/avatar_placeholder.png'

const ARTIST_TYPE_LABELS: Record<ArtistType, string> = {
  [ArtistType.AUTHOR]: 'Auteur',
  [ArtistType.FILM_ACTOR]: 'Acteur',
  [ArtistType.FILM_DIRECTOR]: 'Réalisateur',
  [ArtistType.PERFORMER]: 'Interprète',
  [ArtistType.STAGE_DIRECTOR]: 'Metteur en scène',
}

const ARTIST_THUMB_WIDTH = 44
const ARTIST_DESCRIPTION_MAX_LENGTH = 30

type ArtistOption = ArtistResponseModel & { value: string; label: string }

type ArtistFieldProps = {
  readOnly: boolean
  artistType: ArtistType
  fieldArray: UseFieldArrayReturn<DetailsFormValues, 'artistOfferLinks', 'id'>
}

export function ArtistField({
  readOnly,
  artistType,
  fieldArray,
}: Readonly<ArtistFieldProps>) {
  const {
    setValue,
    watch,
    setFocus,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const { fields, append, remove } = fieldArray

  const fieldsForType = fields
    .map((field, index) => ({ field, index }))
    .filter(({ field }) => field.artistType === artistType)

  const removeEntry = (indexToRemove: number) => {
    assertOrFrontendError(
      fieldsForType.length > 1,
      '`removeEntry` should not be called when there is only one entry of this type.'
    )

    const currentPosInType = fieldsForType.findIndex(
      ({ index }) => index === indexToRemove
    )

    remove(indexToRemove)

    if (currentPosInType > 0) {
      const prevFieldInType = fieldsForType[currentPosInType - 1]
      setFocus(`artistOfferLinks.${prevFieldInType.index}.artistName`)
    } else {
      const nextFieldInType = fieldsForType[1]
      setFocus(`artistOfferLinks.${nextFieldInType.index - 1}.artistName`)
    }
  }

  return (
    <>
      {fieldsForType.map(({ field, index }) => {
        const name = `artistOfferLinks.${index}`
        const artistName = watch(`artistOfferLinks.${index}.artistName`)
        const isTrashDisabled =
          fieldsForType.length === 1 && !artistName?.trim()

        return (
          <div key={field.id} className={styles.row}>
            <div className={styles.select}>
              <ApiSelect<ArtistOption>
                name={name}
                label={ARTIST_TYPE_LABELS[artistType]}
                onSelect={(artist: ArtistOption | undefined) => {
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
                onCreate={(artistName) => {
                  setValue(
                    `artistOfferLinks.${index}`,
                    {
                      artistId: undefined,
                      artistName: artistName,
                      artistType,
                    },
                    { shouldValidate: true }
                  )
                }}
                onReset={() => {
                  setValue(
                    `artistOfferLinks.${index}`,
                    { artistId: undefined, artistName: '', artistType },
                    { shouldValidate: true }
                  )
                }}
                searchApi={async (searchText) => {
                  const artists = await api.getArtists({
                    query: { search: searchText },
                  })

                  return artists.map((artist) => ({
                    ...artist,
                    value: artist.id,
                    label: artist.name,
                    description: artist.description
                      ? truncateAtWord(
                          artist.description,
                          ARTIST_DESCRIPTION_MAX_LENGTH
                        )
                      : null,
                    thumbUrl: artist.thumbUrl
                      ? resizeImageURL({
                          imageURL: artist.thumbUrl,
                          width: ARTIST_THUMB_WIDTH,
                        })
                      : null,
                  }))
                }}
                error={errors?.artistOfferLinks?.[index]?.artistName?.message}
                minSearchLength={2}
                disabled={readOnly}
                required={false}
                thumbPlaceholder={avatarPlaceholder}
                value={artistName}
              />
            </div>

            {!readOnly && fieldsForType.length > 1 && (
              <div className={styles['button-action']}>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullTrashIcon}
                  iconAlt={'Supprimer ce champ'}
                  onClick={() => removeEntry(index)}
                  disabled={isTrashDisabled}
                />
              </div>
            )}
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
              { artistId: undefined, artistName: '', artistType },
              { shouldFocus: true }
            )
          }
        />
      )}
    </>
  )
}

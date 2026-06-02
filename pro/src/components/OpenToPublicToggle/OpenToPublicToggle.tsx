import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'

export interface OpenToPublicToggleProps {
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  isOpenToPublic?: string | null
  error?: string
  showDescription?: boolean
  overrideDescription?: string
}

export const OpenToPublicToggle = ({
  onChange,
  isOpenToPublic,
  error,
  overrideDescription,
}: OpenToPublicToggleProps): JSX.Element => {
  return (
    <RadioButtonGroup
      name="isOpenToPublic"
      label="Disposez-vous d'un lieu ouvert au public ?"
      {...(overrideDescription ? { description: overrideDescription } : {})}
      variant="detailed"
      error={error}
      options={[
        {
          label: "Oui, j'ai un lieu fixe ouvert au public",
          description:
            'Le public se rend dans un local à ma disposition : salle, boutique, musée, cinéma…',
          value: 'true',
        },
        {
          label: "Non, je n'ai pas de lieu fixe ouvert au public",
          description:
            "J'interviens en ligne, chez des tiers ou de façon ponctuelle : cinéma itinérant, spectacles...",
          value: 'false',
        },
      ]}
      onChange={onChange}
      checkedOption={isOpenToPublic?.toString()}
    />
  )
}

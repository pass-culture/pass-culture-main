import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'

export interface OpenToPublicToggleProps {
  className?: string
  radioDescriptions?: {
    yes?: string
    no?: string
  }
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  isOpenToPublic?: string | null
  showDescription?: boolean
}

const DEFAULT_RADIO_DESCRIPTIONS: OpenToPublicToggleProps['radioDescriptions'] =
  {
    yes: 'Votre adresse postale sera visible.',
    no: 'Votre adresse postale ne sera pas visible.',
  }

export const OpenToPublicToggle = ({
  className,
  radioDescriptions = {},
  onChange,
  isOpenToPublic,
  showDescription = true,
}: OpenToPublicToggleProps): JSX.Element => {
  const finalRadioDescriptions = {
    ...DEFAULT_RADIO_DESCRIPTIONS,
    ...radioDescriptions,
  }

  const description =
    isOpenToPublic === 'true'
      ? finalRadioDescriptions.yes
      : isOpenToPublic === 'false'
        ? finalRadioDescriptions.no
        : ''

  return (
    <RadioButtonGroup
      name="isOpenToPublic"
      className={className}
      label="Accueillez-vous du public dans votre structure ?"
      {...(showDescription ? { description } : {})}
      variant="detailed"
      sizing="hug"
      options={[
        {
          label: 'Oui',
          value: 'true',
        },
        {
          label: 'Non',
          value: 'false',
        },
      ]}
      display="horizontal"
      onChange={onChange}
      checkedOption={isOpenToPublic?.toString()}
    />
  )
}

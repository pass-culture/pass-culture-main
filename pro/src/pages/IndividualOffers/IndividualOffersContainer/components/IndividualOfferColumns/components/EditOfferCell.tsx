import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import penIcon from '@/icons/full-edit.svg'
import { DropdownItem } from '@/ui-kit/DropdownMenuWrapper/DropdownItem'

interface EditOfferCellProps {
  editionOfferLink: string
}

export const EditOfferCell = ({ editionOfferLink }: EditOfferCellProps) => {
  return (
    <DropdownItem>
      <Button
        as="a"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        to={editionOfferLink}
        icon={penIcon}
        label="Voir l’offre"
      />
    </DropdownItem>
  )
}

import { Button } from '@/design-system/Button/Button'
import penIcon from '@/icons/full-edit.svg'
import { DropdownItem } from '@/ui-kit/DropdownMenuWrapper/DropdownItem'

interface EditOfferCellProps {
  editionOfferLink: string
}

export const EditOfferCell = ({ editionOfferLink }: EditOfferCellProps) => {
  return (
    <DropdownItem asChild>
      <Button
        as="a"
        to={editionOfferLink}
        icon={penIcon}
        label="Voir l’offre"
      />
    </DropdownItem>
  )
}

import penIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'

interface EditOfferCellProps {
  editionOfferLink: string
}

export const EditOfferCell = ({ editionOfferLink }: EditOfferCellProps) => {
  return (
    <DropdownItem asChild>
      <ButtonLink to={editionOfferLink} icon={penIcon}>
        Voir l’offre
      </ButtonLink>
    </DropdownItem>
  )
}

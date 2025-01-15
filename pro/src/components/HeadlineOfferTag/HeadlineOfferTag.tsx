import fullBoostedIcon from 'icons/full-boosted.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

type HeadlineOfferTagProps = {
  className?: string
}

export const HeadlineOfferTag = ({ className }: HeadlineOfferTagProps) => {
  return (
    <Tag
      variant={TagVariant.SMALL_OUTLINE}
      className={className}
    >
      <SvgIcon
        src={fullBoostedIcon}
        width="20"
      />
      Offre à la une
    </Tag>
  )
}
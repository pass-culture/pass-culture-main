import { Banner } from '@/design-system/Banner/Banner'

interface Props {
  className?: string
}

export const BannerPublicApi = ({ className }: Props): JSX.Element => (
  <div className={className}>
    <Banner
      title="Import automatique"
      description="Cette offre a été importée automatiquement depuis votre système de billetterie."
    />
  </div>
)

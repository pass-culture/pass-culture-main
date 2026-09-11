export enum InfoPanelSurface {
  FLAT = 'flat',
  ELEVATED = 'elevated',
}

export enum InfoPanelVariant {
  ORDERED = 'ordered',
  UNORDERED = 'unordered',
}

export enum InfoPanelSize {
  LARGE = 'large',
  SMALL = 'small',
}

type OrderedInfoPanel = {
  title: string
  description: string | JSX.Element
  icon?: never
  iconAlt?: never
}

type UnorderedInfoPanel = {
  title: string
  description: string | JSX.Element
  icon: string
  iconAlt?: string
}

type BaseInfoPanelListProps = {
  surface: InfoPanelSurface.FLAT | InfoPanelSurface.ELEVATED
  size?: InfoPanelSize
  titleLevel?: '2' | '3'
}

type OrderedInfoPanelListProps = BaseInfoPanelListProps & {
  variant: InfoPanelVariant.ORDERED
  panels: OrderedInfoPanel[]
}

type UnorderedInfoPanelListProps = BaseInfoPanelListProps & {
  variant: InfoPanelVariant.UNORDERED
  panels: UnorderedInfoPanel[]
}

export type InfoPanelListProps =
  | OrderedInfoPanelListProps
  | UnorderedInfoPanelListProps

export type InfoPanelItemProps =
  | {
      variant: InfoPanelVariant.ORDERED
      panel: OrderedInfoPanel
      index: number
      Heading: 'h2' | 'h3'
    }
  | {
      variant: InfoPanelVariant.UNORDERED
      panel: UnorderedInfoPanel
      index: number
      Heading: 'h2' | 'h3'
    }

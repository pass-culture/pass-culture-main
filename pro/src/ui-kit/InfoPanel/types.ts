export enum InfoPanelSurface {
  FLAT = 'flat',
  ELEVATED = 'elevated',
}

export enum InfoPanelSize {
  LARGE = 'large',
  SMALL = 'small',
}

type BaseProps = {
  title: string
  children: string | JSX.Element
  surface: InfoPanelSurface.FLAT | InfoPanelSurface.ELEVATED
  size?: InfoPanelSize
}

type FlatProps = {
  icon: string
  iconAlt?: string
  stepNumber?: never
}

type ElevatedProps = {
  icon?: never
  iconAlt?: never
  stepNumber: number
}

export type InfoPanelProps = BaseProps & (FlatProps | ElevatedProps)

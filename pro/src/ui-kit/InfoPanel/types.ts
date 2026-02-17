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
  size?: InfoPanelSize
}

type FlatProps = {
  surface: InfoPanelSurface.FLAT
  icon: string
  iconAlt: string
}

type ElevatedProps = {
  surface: InfoPanelSurface.ELEVATED
  stepNumber: number
}

export type InfoPanelProps = BaseProps & (FlatProps | ElevatedProps)

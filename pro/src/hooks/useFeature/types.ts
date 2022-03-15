export interface IUseFeature {
  initialized: boolean
  isActive?: boolean
}

export interface IFeature {
  nameKey: string
  isActive: boolean
}

export interface IFeatureList {
  initialized: boolean
  list: IFeature[]
}

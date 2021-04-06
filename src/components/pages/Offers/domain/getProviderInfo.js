export const getProviderInfo = providerName => {
  const providers = [
    {
      id: 'allociné',
      icon: 'logo-allocine',
      name: 'Allociné',
    },
    {
      id: 'leslibraires.fr',
      icon: 'logo-libraires',
      name: 'Leslibraires.fr',
    },
    {
      id: 'titelive',
      icon: 'logo-titeLive',
      name: 'Tite Live',
    },
    {
      id: 'fnac',
      icon: 'logo-fnac',
      name: 'Fnac',
    },
    {
      id: 'praxiel',
      icon: 'logo-praxiel',
      name: 'Praxiel',
    },
    {
      id: 'librisoft',
      icon: 'logo-librisoft',
      name: 'Librisoft',
    },
  ]

  return providers.find(providerInfo => providerName.toLowerCase().startsWith(providerInfo.id))
}

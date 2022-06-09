export const getProviderInfo = providerName => {
  const providers = [
    {
      id: 'allociné',
      icon: 'logo-allocine',
      name: 'Allociné',
      synchronizedOfferMessage: 'Offre synchronisée avec Allociné',
    },
    {
      id: 'leslibraires.fr',
      icon: 'logo-libraires',
      name: 'Leslibraires.fr',
      synchronizedOfferMessage: 'Offre synchronisée avec Leslibraires.fr',
    },
    {
      id: 'titelive',
      icon: 'logo-titeLive',
      name: 'Tite Live',
      synchronizedOfferMessage: 'Offre synchronisée avec Tite Live',
    },
    {
      id: 'fnac',
      icon: 'logo-fnac',
      name: 'Fnac',
      synchronizedOfferMessage: 'Offre synchronisée avec Fnac',
    },
    {
      id: 'mollat',
      icon: 'logo-cdi-bookshop',
      name: 'Mollat',
      synchronizedOfferMessage: 'Offre synchronisée avec Mollat',
    },
    {
      id: 'cdi-bookshop',
      icon: 'logo-cdi-bookshop',
      name: 'CDI-Bookshop',
      synchronizedOfferMessage: 'Offre synchronisée avec CDI-Bookshop',
    },
    {
      id: 'tmic-ellipses',
      icon: 'logo-tmic-ellipses',
      name: 'TMIC Ellipses',
      synchronizedOfferMessage: 'Offre synchronisée avec TMIC Ellipses',
    },
    {
      id: 'praxiel',
      icon: 'logo-praxiel',
      name: 'Praxiel',
      synchronizedOfferMessage: 'Offre synchronisée avec Praxiel',
    },
    {
      id: 'librisoft',
      icon: 'logo-librisoft',
      name: 'Librisoft',
      synchronizedOfferMessage: 'Offre synchronisée avec Librisoft',
    },
    {
      id: 'decitre',
      icon: 'logo-decitre',
      name: 'Decitre',
      synchronizedOfferMessage: 'Offre synchronisée avec Decitre',
    },
    {
      id: 'pass',
      icon: 'logo-pass-culture-dark',
      name: 'Pass Culture API Stocks',
      synchronizedOfferMessage: 'Offre importée automatiquement',
    },
    {
      id: 'ciné office',
      icon: 'logo-cine-digital-service',
      name: 'Ciné Office',
      synchronizedOfferMessage: 'Offre synchronisée avec Ciné Office',
    }
  ]

  return providers.find(providerInfo =>
    providerName.toLowerCase().startsWith(providerInfo.id)
  )
}

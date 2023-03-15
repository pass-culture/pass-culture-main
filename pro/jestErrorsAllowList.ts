// DO NOT ADD ERRORS TO THIS LIST!
// We should remove it progressively
export default [
  { error: '', files: [''] },
  {
    error: 'Error: Not implemented: HTMLFormElement.prototype.submit',
    files: [''],
  },
  {
    error: 'Error: Not implemented: navigation (except hash changes)',
    files: [''],
  },
  {
    error:
      'Warning: An update to %s inside a test was not wrapped in act(...).',
    files: [
      'components/CollectiveOfferSummary/components/CollectiveOfferPracticalInformation/CollectiveOfferPracticalInformation.tsx',
      'components/RouteLeavingGuard/RouteLeavingGuard.tsx',
      'components/VenueForm/EACInformation/CollectiveData/CollectiveData.tsx',
      'screens/OfferIndividual/Informations/Informations.tsx',
      'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/Offers.tsx',
      '',
    ],
  },
  {
    error:
      "Warning: Can't perform a React state update on an unmounted component. This is a no-op, but it indicates a memory leak in your application. To fix, cancel all subscriptions and asynchronous tasks in %s.%s",
    files: [
      'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/DeleteVenueProviderButton/DeleteVenueProviderButton.tsx',
      'screens/OfferIndividual/Informations/Informations.tsx',
      'screens/OfferIndividual/StocksEvent/StocksEvent.tsx',
      'screens/OfferIndividual/StocksThing/StocksThing.tsx',
      'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/OffersSearch.tsx',
      'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/Offers.tsx',
      'pages/AdageIframe/app/providers/AnalyticsContextProvider.tsx',
      'context/OfferIndividualContext/OfferIndividualContext.tsx',
      '',
    ],
  },
  {
    error:
      'Warning: You seem to have overlapping act() calls, this is not supported. Be sure to await previous act() calls before making a new one. ',
    files: [''],
  },
]

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
    error: 'Error: Not implemented: window.scrollTo',
    files: ['app/App/App.tsx', ''],
  },
  {
    error: "Error: Uncaught 'Error: Not implemented: window.scrollTon' +",
    files: ['app/App/App.tsx', ''],
  },
  {
    error:
      "Error: Uncaught 'Warning: A component is changing an uncontrolled input to be controlled. This is likely caused by the value changing from undefined to a defined value, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components%s'",
    files: [''],
  },
  {
    error: "Error: Uncaught [Error: Le statut de l'offre n'est pas valide]",
    files: [''],
  },
  {
    error: 'Error: Uncaught [Error: Should not already be working.]',
    files: [''],
  },
  {
    error: 'Error: Uncaught [Error: Unsupported step type: UNKNOWN]',
    files: [''],
  },
  {
    error:
      'Warning: A component is changing an uncontrolled input to be controlled. This is likely caused by the value changing from undefined to a defined value, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components%s',
    files: ['ui-kit/form/shared/BaseInput/BaseInput.tsx', ''],
  },
  {
    error:
      'Warning: An update to %s inside a test was not wrapped in act(...).',
    files: [
      'components/CollectiveOfferSummary/components/CollectiveOfferPracticalInformation/CollectiveOfferPracticalInformation.tsx',
      'components/RouteLeavingGuard/RouteLeavingGuard.tsx',
      'components/VenueForm/EACInformation/CollectiveData/CollectiveData.tsx',
      'screens/OfferIndividual/Informations/Informations.tsx',
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
      '',
    ],
  },
  {
    error:
      'Warning: Use the `defaultValue` or `value` props on <select> instead of setting `selected` on <option>.%s',
    files: [
      'screens/Bookings/BookingsRecapTable/components/Filters/FilterByOmniSearch/FilterByOmniSearch.tsx',
      '',
    ],
  },
  {
    error:
      'Warning: You seem to have overlapping act() calls, this is not supported. Be sure to await previous act() calls before making a new one. ',
    files: [''],
  },
  {
    error:
      'Warning: validateDOMNesting(...): %s cannot appear as a child of <%s>.%s%s%s',
    files: [
      'pages/Offers/Offers/OfferItem/Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell.tsx',
      'pages/Offers/Offers/OfferItem/Cells/OfferNameCell/OfferNameCell.tsx',
      'ui-kit/Divider/Divider.tsx',
      '',
    ],
  },
]

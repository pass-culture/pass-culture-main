// DO NOT ADD ERRORS TO THIS LIST!
// We should remove it progressively
export default [
  {
    error:
      'Warning: Cannot update during an existing state transition (such as within `render`). Render methods should be a pure function of props and state.%s',
    files: [
      'pages/VenueEdition/VenueEdition.tsx',
      'screens/SignupJourneyForm/Validation/Validation.tsx',
    ],
  },
  {
    error:
      'Warning: Cannot update a component (`%s`) while rendering a different component (`%s`). To locate the bad setState() call inside `%s`, follow the stack trace as described in https://reactjs.org/link/setstate-in-render%s',
    files: [
      'pages/VenueEdition/VenueEdition.tsx',
      'screens/SignupJourneyForm/Validation/Validation.tsx',
    ],
  },
  // This error exists in the following test:
  // src/pages/OfferIndividualWizard/Confirmation/__specs__/Confirmation.spec.tsx
  // It exists because we click on an anchor tag (<a>) and assert that the tracking
  // is called.
  // However Jest doesn't support navigation changes and we shouldn't click on links in tests
  // Furthermore, we shouldn't have to manually track page changes as Google Analytics
  // should do this out of the box. So the real good solution here is:
  // - check why we manually track page changes with the data team
  // - remove all trackers used to track page changes
  // - remove the offending test
  {
    error: 'Error: Not implemented: navigation (except hash changes)',
    files: [''],
  },
]

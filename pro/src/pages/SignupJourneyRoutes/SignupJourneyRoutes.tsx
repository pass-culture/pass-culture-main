import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers } from 'screens/SignupJourneyForm/Offerers'

const SignupJourneyRoutes = () => {
  return (
    <SignupJourneyContextProvider>
      <SignupJourneyFormLayout>
        <Routes>
          <Route path={'/structure'} element={<Offerer />} />
          <Route path={'/structures'} element={<Offerers />} />
          <Route
            path={'/authentification'}
            element={<OffererAuthentication />}
          />
          <Route path={'/activite'} element={<Activity />} />
          <Route path={'/validation'} element={<div>Validation</div>} />
        </Routes>
      </SignupJourneyFormLayout>
    </SignupJourneyContextProvider>
  )
}

export default SignupJourneyRoutes

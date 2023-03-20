import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers } from 'screens/SignupJourneyForm/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome'

const SignupJourneyRoutes = () => {
  return (
    <SignupJourneyContextProvider>
      <SignupJourneyFormLayout>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/structure" element={<Offerer />} />
          <Route path="/structure/rattachement" element={<Offerers />} />
          <Route
            path="/structure/rattachement/confirmation"
            element={<ConfirmedAttachment />}
          />
          <Route path="/authentification" element={<OffererAuthentication />} />
          <Route path="/activite" element={<Activity />} />
          <Route path="/validation" element={<Validation />} />
        </Routes>
      </SignupJourneyFormLayout>
    </SignupJourneyContextProvider>
  )
}

export default SignupJourneyRoutes

import * as firebase from '@firebase/app'
import { getFirestore, collection, getDocs } from '@firebase/firestore/lite'
import React from 'react'
import Joyride from 'react-joyride'
import type { Placement } from 'react-joyride'

import useAnalytics from 'components/hooks/useAnalytics'

// Get a list of cities from your database
async function getCities(db: any) {
  const citiesCol = collection(db, 'emails')
  const citySnapshot = await getDocs(citiesCol)
  const cityList = citySnapshot.docs.map((doc: any) => doc.data())
  return cityList
}

const StepByStepTutorial = (): JSX.Element => {
  const { app: firebaseApp } = useAnalytics()

  if (firebaseApp !== null) {
    const firebaseDb: any = getFirestore(firebaseApp)
    console.log('StepByStepTutorial')
    getCities(firebaseDb)
      .then((response: any) => console.log('response', response))
      .catch((error: any) => console.log('error', error))
      .finally(() => console.log('done'))
  }

  const tutorial = {
    steps: [
      {
        target: '[data-tutorialid="breadcrumb-offerers"]',
        // target: '.pc-breadcrumb',
        placementBeacon: 'left' as Placement,
        content: 'lien structure !',
      },
      {
        target: '[data-tutorialid="breadcrumb-profile"]',
        // target: '.pc-breadcrumb',
        placementBeacon: 'left' as Placement,
        content: 'lien structure !',
      },
      {
        target: '.h-support',
        // target: '.pc-breadcrumb',
        placementBeacon: 'left' as Placement,
        content: 'i did scroll !',
      },

      // {
      //   target: '.my-other-step',
      //   content: 'This another awesome feature!',
      // },
    ],
  }
  return <Joyride steps={tutorial.steps} continuous run={true} />
}

export default StepByStepTutorial

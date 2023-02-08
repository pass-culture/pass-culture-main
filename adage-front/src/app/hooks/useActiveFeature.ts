import { useContext } from "react";

import { FeaturesContext } from "app/providers/FeaturesContextProvider";

export const useActiveFeature = (featureName: string) => {
  const features = useContext(FeaturesContext);

  return Boolean(
    features.find((feature) => feature.name === featureName)?.isActive
  );
};

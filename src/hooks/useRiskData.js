import { useEffect, useState } from "react";

import { getRiskData, getRainfallData, getSummary, getWarnings } from "@/services/api";

export function useRiskData() {
  const [state, setState] = useState({
    loading: true,
    risk: null,
    rainfall: null,
    summary: null,
    warnings: [],
  });

  useEffect(() => {
    let active = true;
    Promise.all([getRiskData(), getRainfallData(), getSummary(), getWarnings()]).then(
      ([risk, rainfall, summary, warnings]) => {
        if (active) setState({ loading: false, risk, rainfall, summary, warnings });
      },
    );
    return () => {
      active = false;
    };
  }, []);

  return state;
}

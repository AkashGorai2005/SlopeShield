import { useEffect, useMemo, useState } from "react";

import { getLocations } from "@/services/api";

export function useLocations(query = "") {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getLocations().then((res) => {
      if (active) setData(Array.isArray(res) ? res : []);
    }).catch(() => {
      if (active) setData([]);
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => {
      active = false;
    };
  }, []);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return data;
    return data.filter(
      (l) => l.name.toLowerCase().includes(q) || l.state.toLowerCase().includes(q),
    );
  }, [data, query]);

  return { locations: results, all: data, loading };
}

import { useCallback } from "react";
import {
  Link as RouterLink,
  Outlet,
  useLocation as useReactLocation,
  useNavigate as useReactNavigate,
  useParams as useReactParams,
} from "react-router-dom";

export function resolvePath(to, params = {}) {
  let path = String(to ?? "/");
  for (const [key, value] of Object.entries(params)) {
    path = path.replace(`$${key}`, encodeURIComponent(value));
  }
  return path;
}

export function Link({ to = "/", params, hash, children, onClick, ...props }) {
  const target =
    typeof to === "string"
      ? {
          pathname: resolvePath(to, params),
          hash: hash ? `#${hash}` : undefined,
        }
      : {
          ...to,
          hash: hash ? `#${hash}` : to?.hash,
        };

  const handleClick = (event) => {
    if (onClick) onClick(event);
    if (event.defaultPrevented) return;

    if (hash && typeof document !== "undefined") {
      requestAnimationFrame(() => {
        document.getElementById(hash)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  };

  return (
    <RouterLink to={target} onClick={handleClick} {...props}>
      {children}
    </RouterLink>
  );
}

export function useNavigate() {
  const navigate = useReactNavigate();
  return useCallback(
    (target) => {
      if (typeof target === "string") {
        navigate(target);
        return;
      }

      const nextTarget = target && typeof target === "object" ? target : { to: "/" };
      const href = resolvePath(nextTarget.to ?? "/", nextTarget.params ?? {});
      navigate(href);
    },
    [navigate],
  );
}

export function useLocation() {
  return useReactLocation();
}

export function useParams() {
  return useReactParams();
}

export { Outlet };

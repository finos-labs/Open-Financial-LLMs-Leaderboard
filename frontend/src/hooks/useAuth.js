import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { oauthLoginUrl, oauthHandleRedirectIfPresent } from "@huggingface/hub";
import { HF_CONFIG } from "../config/auth";

async function fetchUserInfo(token) {
  const response = await fetch("https://huggingface.co/api/whoami-v2", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch user info");
  }
  return response.json();
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Initialisation de l'authentification
  useEffect(() => {
    let mounted = true;
    const initAuth = async () => {
      try {
        console.group("Auth Initialization");
        setLoading(true);

        // Vérifier s'il y a une redirection OAuth d'abord
        let oauthResult = await oauthHandleRedirectIfPresent();

        // Si pas de redirection, vérifier le localStorage
        if (!oauthResult) {
          const storedAuth = localStorage.getItem(HF_CONFIG.STORAGE_KEY);
          if (storedAuth) {
            try {
              oauthResult = JSON.parse(storedAuth);
              console.log("Found existing auth");
              const userInfo = await fetchUserInfo(oauthResult.access_token);
              if (mounted) {
                setIsAuthenticated(true);
                setUser({
                  username: userInfo.name,
                  token: oauthResult.access_token,
                });
              }
            } catch (err) {
              console.log("Invalid stored auth data, clearing...", err);
              localStorage.removeItem(HF_CONFIG.STORAGE_KEY);
              if (mounted) {
                setIsAuthenticated(false);
                setUser(null);
              }
            }
          }
        } else {
          console.log("Processing OAuth redirect");
          const token = oauthResult.accessToken;
          const userInfo = await fetchUserInfo(token);

          const authData = {
            access_token: token,
            username: userInfo.name,
          };

          localStorage.setItem(HF_CONFIG.STORAGE_KEY, JSON.stringify(authData));

          if (mounted) {
            setIsAuthenticated(true);
            setUser({
              username: userInfo.name,
              token: token,
            });
          }

          // Rediriger vers la page d'origine
          const returnTo = localStorage.getItem("auth_return_to");
          if (returnTo) {
            navigate(returnTo);
            localStorage.removeItem("auth_return_to");
          }
        }
      } catch (err) {
        console.error("Auth initialization error:", err);
        if (mounted) {
          setError(err.message);
          setIsAuthenticated(false);
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
        console.groupEnd();
      }
    };

    initAuth();

    return () => {
      mounted = false;
    };
  }, [navigate, location.pathname]);

  const login = async () => {
    try {
      console.group("Login Process");
      setLoading(true);

      // Sauvegarder la route actuelle pour la redirection post-auth
      const currentRoute = window.location.hash.replace("#", "") || "/";
      localStorage.setItem("auth_return_to", currentRoute);

      // Déterminer l'URL de redirection en fonction de l'environnement
      const redirectUrl =
        window.location.hostname === "localhost" ||
        window.location.hostname === "127.0.0.1"
          ? HF_CONFIG.DEV_URL
          : HF_CONFIG.PROD_URL;

      console.log("Using redirect URL:", redirectUrl);

      // Générer l'URL de login et rediriger
      const loginUrl = await oauthLoginUrl({
        clientId: HF_CONFIG.CLIENT_ID,
        redirectUrl,
        scope: HF_CONFIG.SCOPE,
      });

      window.location.href = loginUrl + "&prompt=consent";

      console.groupEnd();
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message);
      setLoading(false);
      console.groupEnd();
    }
  };

  const logout = () => {
    console.group("Logout Process");
    setLoading(true);
    try {
      console.log("Clearing auth data...");
      localStorage.removeItem(HF_CONFIG.STORAGE_KEY);
      localStorage.removeItem("auth_return_to");
      setIsAuthenticated(false);
      setUser(null);
      console.log("Logged out successfully");
    } catch (err) {
      console.error("Logout error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
      console.groupEnd();
    }
  };

  return {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    logout,
  };
}

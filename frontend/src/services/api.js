const getBaseUrl = () => {
  if (typeof window !== "undefined" && window.location.port && window.location.port !== "5000") {
    return "http://127.0.0.1:5000";
  }
  return "";
};

export const EMP_API = {
  baseUrl: getBaseUrl(),
  resolveUrl(path) {
    if (!path) return "";
    if (path.startsWith("http://") || path.startsWith("https://")) return path;
    return `${getBaseUrl()}${path}`;
  },
  getToken() {
    return localStorage.getItem("emp_v2_token") || "";
  },
  setToken(token) {
    if (token) {
      localStorage.setItem("emp_v2_token", token);
    } else {
      localStorage.removeItem("emp_v2_token");
    }
  },

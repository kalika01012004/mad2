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
  getUser() {
    try {
      const raw = localStorage.getItem("emp_v2_user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  setUser(usr) {
    if (usr) {
      localStorage.setItem("emp_v2_user", JSON.stringify(usr));
    } else {
      localStorage.removeItem("emp_v2_user");
    }
  },
  async request(path, opts = {}) {
    const token = this.getToken();
    const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const url = this.resolveUrl(path);
    const res = await fetch(url, { ...opts, headers });
    let body = {};
    try {
      body = await res.json();
    } catch {
      body = {};
    }
    if (!res.ok) {
      throw new Error(body.error || body.msg || `Request failed (${res.status})`);
    }
    return body;
  },
  get(path) {
    return this.request(path, { method: "GET" });
  },
  post(path, payload = {}) {
    return this.request(path, { method: "POST", body: JSON.stringify(payload) });
  },
  put(path, payload = {}) {
    return this.request(path, { method: "PUT", body: JSON.stringify(payload) });
  },
  delete(path) {
    return this.request(path, { method: "DELETE" });
  },
};

export default EMP_API;

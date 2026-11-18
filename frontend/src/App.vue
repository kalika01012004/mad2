<template>
  <div>
    <div class="toast-container-fixed">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['alert', 'alert-' + t.type, 'shadow-sm', 'd-flex', 'align-items-center', 'py-2', 'px-3', 'mb-2']"
        role="alert"
      >
        <i class="bi bi-info-circle-fill me-2"></i>
        <div class="small fw-medium">{{ t.message }}</div>
      </div>
    </div>

    <nav class="navbar navbar-expand-lg navbar-dark navbar-emp sticky-top py-2">
      <div class="container-fluid px-3 px-lg-4">
        <a class="navbar-brand d-flex align-items-center fw-bold" href="#">
          <i class="bi bi-mortarboard-fill fs-4 me-2 text-info"></i>
          <span>EMP <span class="badge bg-primary ms-1">V2</span></span>
          <span class="d-none d-md-inline ms-2 fw-normal fs-6 text-light opacity-75">
            | Examination Management Portal
          </span>
        </a>

        <div class="d-flex align-items-center gap-2">
          <template v-if="user">
            <div class="position-relative">
              <button class="btn btn-sm btn-light position-relative" @click="showNotifPanel = !showNotifPanel">
                <i class="bi bi-bell-fill text-primary"></i>
                <span
                  v-if="unreadCount > 0"
                  class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                >
                  {{ unreadCount }}
                </span>
              </button>
            </div>

            <button class="btn btn-sm btn-outline-info text-white" @click="showProfileModal = true">
              <i class="bi bi-person-circle me-1"></i>
              <span class="d-none d-sm-inline">{{ user.name }}</span>
              <span class="badge bg-warning text-dark ms-1 text-uppercase">{{ user.role }}</span>
            </button>

            <button class="btn btn-sm btn-danger" @click="logout">
              <i class="bi bi-box-arrow-right me-1"></i>Logout
            </button>
          </template>
        </div>
      </div>
    </nav>

    <div
      v-if="user && showNotifPanel"
      class="card shadow-lg position-fixed"
      style="top: 62px; right: 20px; width: 370px; max-height: 480px; z-index: 1500; overflow-y: auto;"
    >
      <div class="card-header bg-white d-flex justify-content-between align-items-center py-2">
        <h6 class="mb-0 fw-bold"><i class="bi bi-bell me-1 text-primary"></i>Notifications</h6>
        <div>
          <button class="btn btn-link btn-sm text-decoration-none p-0 me-2" @click="markAllRead">Mark all read</button>
          <button class="btn-close btn-sm" @click="showNotifPanel = false"></button>
        </div>
      </div>
      <div class="list-group list-group-flush">
        <div v-if="notifications.length === 0" class="p-3 text-center text-muted small">
          No notifications yet.
        </div>
        <div
          v-for="n in notifications"
          :key="n.id"
          :class="['list-group-item', !n.is_read ? 'bg-light' : '']"
        >
          <div class="d-flex justify-content-between">
            <strong class="small text-primary">{{ n.title }}</strong>
            <span class="badge bg-secondary">{{ n.notif_type }}</span>
          </div>
          <p class="small mb-1 text-secondary mt-1">{{ n.message }}</p>
          <a v-if="n.action_url" :href="resolveUrl(n.action_url)" target="_blank" class="btn btn-xs btn-outline-primary btn-sm py-0 px-2">
            <i class="bi bi-download me-1"></i>Download
          </a>
        </div>
      </div>
    </div>

    <AuthView
      v-if="!user"
      @authenticated="onAuthenticated"
      @notify="notify"
    />

    <AdminPortal
      v-else-if="user.role === 'admin'"
      @notify="notify"
      @refresh-notifications="loadNotifications"

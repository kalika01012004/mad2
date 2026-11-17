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

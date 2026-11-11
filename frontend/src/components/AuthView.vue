<template>
  <div class="container py-4 py-lg-5">
    <div class="row g-4 align-items-stretch">
      <div class="col-lg-6">
        <div class="auth-hero p-4 p-lg-5 h-100 d-flex flex-column justify-content-between shadow">
          <div>
            <span class="badge bg-info text-dark mb-3 px-3 py-2 fw-semibold">
              Examination Management Portal
            </span>
            <h1 class="fw-bold display-6 mb-3">EMP — V2</h1>
            <p class="lead opacity-90 mb-4">
              Manage course examinations, examiner slot schedules, student slot bookings, rubric evaluations, and result scorecards in one place.
            </p>
            <div class="row g-3">
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-shield-lock-fill text-warning me-2"></i>Admin</h6>
                  <small class="opacity-75">Courses, timelines, rubrics, rescheduling &amp; reports</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-person-workspace text-info me-2"></i>Examiner</h6>
                  <small class="opacity-75">Slot creation &amp; rubric evaluation</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-calendar2-check text-success me-2"></i>Student</h6>
                  <small class="opacity-75">Slot booking, CSV history export &amp; PDF scorecards</small>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="p-3 rounded bg-white bg-opacity-10">
                  <h6 class="fw-bold mb-1"><i class="bi bi-lightning-charge-fill text-danger me-2"></i>Batch Jobs</h6>
                  <small class="opacity-75">Daily reminders, monthly reports &amp; Redis cache</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card section-card p-4 p-lg-5 h-100">
          <ul class="nav nav-pills nav-fill mb-4 bg-light p-1 rounded-3">
            <li class="nav-item">
              <button
                :class="['nav-link', authTab === 'login' ? 'active' : '']"
                @click="authTab = 'login'"
              >
                <i class="bi bi-box-arrow-in-right me-1"></i>Login
              </button>
            </li>
            <li class="nav-item">
              <button
                :class="['nav-link', authTab === 'register' ? 'active' : '']"
                @click="authTab = 'register'"
              >
                <i class="bi bi-person-plus me-1"></i>Student Register
              </button>
            </li>
          </ul>

          <form v-if="authTab === 'login'" @submit.prevent="handleLogin" novalidate>
            <h4 class="fw-bold mb-1">Sign In</h4>
            <p class="text-muted small mb-4">
              Log in as Admin, Examiner, or Student.
            </p>
            <div class="mb-3">
              <label class="form-label fw-medium">Email or Username <span class="text-danger">*</span></label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                <input
                  type="text"
                  class="form-control"
                  v-model.trim="loginForm.identifier"
                  placeholder="Enter your email or username"
                  required
                />
              </div>
            </div>
            <div class="mb-4">
              <label class="form-label fw-medium">Password <span class="text-danger">*</span></label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-key"></i></span>
                <input
                  type="password"
                  class="form-control"
                  v-model="loginForm.password"
                  placeholder="Enter your password"
                  required
                  minlength="6"
                />
              </div>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2 fw-semibold" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Sign In
            </button>
          </form>

          <form v-else @submit.prevent="handleRegister">
            <h4 class="fw-bold mb-1">Student Registration</h4>
            <div class="alert alert-info py-2 small mb-3">
              Only students can self-register. Examiners are added by the Admin.
            </div>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label small fw-medium">Full Name <span class="text-danger">*</span></label>
